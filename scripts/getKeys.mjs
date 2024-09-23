/**
 * @fileoverview A utility script to process JSON responses and determine object
 * trees for a series of USGS Design Spectras from different design standards.
 * @author jbronder
 */

import {readdir, readFile} from 'node:fs/promises';
import {parse} from 'node:path';
import {cwd, exit} from 'node:process';

try {
  let fileList = await extractJsonFiles();
  console.log(fileList);

  let commonTree = await findIntersectingKeys(fileList);
  console.log('commonTree:', commonTree);

  let allTree = await findUnionKeys(fileList);
  console.log('allTree:', allTree);

} catch (err) {
  console.error(err);
}

/**
 * Produces a list of files that contain "...response.json" files in the current
 * working directory
 * @async
 * @returns {Promise<string[]>}
 */
async function extractJsonFiles() {
  try {
    const files = await readdir(cwd());
    const jsonFiles = [];
    for (const f of files) {
      let pathObj = parse(f);
      if (pathObj.base.includes('response') && pathObj.ext === '.json') {
        jsonFiles.push(f);
      }
    }
    return jsonFiles;
  } catch (err) {
    throw err;
  }
}

/**
 * Generates an object who's structure contains the set of common properties and
 * their nested object trees
 * @async
 * @param {string[]} jsonFiles - a list of file names that are JSON response
 * files from USGS
 * @returns {Promise<Object>}
 */
async function findIntersectingKeys(jsonFiles) {
  try {
    if (!Array.isArray(jsonFiles)) {
      throw new TypeError('argument is not an Array.');
    }

    if (jsonFiles.length === 0) {
      throw new Error(`Array is empty.`);
    } else if (jsonFiles.length === 1) {
      const file = await readFile(jsonFiles[0], 'utf8');
      const jsonData = JSON.parse(file);
      return enumerateKeyTree(jsonData);
    } else {
      const firstFile = await readFile(jsonFiles[0], 'utf8');
      const secondFile = await readFile(jsonFiles[1], 'utf8');
      const jsonFirst = JSON.parse(firstFile);
      const jsonSecond = JSON.parse(secondFile);
      let resultTree = intersectKeys(jsonFirst, jsonSecond);
      for (let i = 2; i < jsonFiles.length; ++i) {
        const otherFile = await readFile(jsonFiles[i], 'utf8');
        const jsonOther = JSON.parse(otherFile);
        resultTree = intersectKeys(resultTree, jsonOther);
      }
      return resultTree;
    }
  } catch (err) {
    throw err;
  }
}

/**
 * Generates an object who's structure contains the set of all possible
 * properties and their nested object trees
 * @async
 * @param {string[]} jsonFiles - a list of JSON files that are JSON response
 * files from USGS
 * @return {Promise<Object>}
 */
async function findUnionKeys(jsonFiles) {
  try {
    if (!Array.isArray(jsonFiles)) {
      throw new TypeError('argument is not an Array.');
    }

    if (jsonFiles.length === 0) {
      throw new Error(`Array is empty.`);
    } else if (jsonFiles.length === 1) {
      const file = await readFile(jsonFiles[0], 'utf8');
      const jsonData = JSON.parse(file);
      return enumerateKeyTree(jsonData);
    } else {
      const firstFile = await readFile(jsonFiles[0], 'utf8');
      const secondFile = await readFile(jsonFiles[1], 'utf8');
      const jsonFirst = JSON.parse(firstFile);
      const jsonSecond = JSON.parse(secondFile);
      let resultTree = unionKeys(jsonFirst, jsonSecond);
      for (let i = 2; i < jsonFiles.length; ++i) {
        const otherFile = await readFile(jsonFiles[i], 'utf8');
        const jsonOther = JSON.parse(otherFile);
        resultTree = unionKeys(resultTree, jsonOther);
      }
      return resultTree;
    }
  } catch (err) {
    throw err;
  }
}

/**
 * Produce an object tree of all properties and their nested object trees. The
 * function also sets null to properties that contain primitives and Array
 * values
 * @param {Object} o - parsed JSON into an object; essentially an object
 * @return {Object} - the resultant object tree containing possble nested
 * objects and primitives and Array values nulled out.
 */
function enumerateKeyTree(o) {
  const keyTree = {};
  enumerateKeyTreeHelper(o, keyTree);
  return keyTree;
}

/**
 * Helper function that populates a plain JS object with keys
 * @param {Object} o - input JS object that may contain nested JS object
 * @param {Object} tree - a JS object that contains the resultant object tree
 */
function enumerateKeyTreeHelper(o, tree) {
  for (const [key, val] of Object.entries(o)) {
    if (!isObject(val)) {
      tree[key] = null;
    } else {
      let subTree = {};
      tree[key] = subTree;
      enumerateKeyTreeHelper(o[key], subTree);
    }
  }
}

/**
 * Returns an object tree containing the intersection of keys in an object tree
 * @param {Object} first
 * @param {Object} second
 * @return {Object}
 */
function intersectKeys(first, second) {
  let result = {};
  intersectKeysHelper(first, second, result);
  return result;
}

/**
 * Intersection key tree helper function
 * @param {Object} first
 * @param {Object} second
 * @param {Object} resultantTree
 */
function intersectKeysHelper(first, second, resultantTree) {
  let firstSet = new Set(Object.keys(first));
  let secondSet = new Set(Object.keys(second));
  let intersect = firstSet.intersection(secondSet);
  if (intersect.size !== 0) {
    for (const prop of intersect.values()) {
      if (!isObject(first[prop])) {
        resultantTree[prop] = null;
      } else {
        let subTree = {};
        resultantTree[prop] = subTree;
        intersectKeysHelper(first[prop], second[prop], subTree);
      }
    }
  }
}

/**
 * Returns a object tree containing a union of all keys between the 'first' and
 * 'second' key trees
 * @param {Object} first - first key tree
 * @param {Object} second - second key tree
 */
function unionKeys(first, second) {
  let result = {};
  unionKeysHelper(first, second, result);
  return result;
}

/**
 * Union key tree helper function
 * @param {Object} first - first key tree
 * @param {Object} second - second key tree
 * @param {Object} resultantTree
 */
function unionKeysHelper(first, second, resultantTree) {
  let firstSet = new Set(Object.keys(first));
  let secondSet = new Set(Object.keys(second));
  let union = firstSet.union(secondSet);
  if (union.size !== 0) {
    for (const prop of union.values()) {
      if (!isObject(first[prop]) || !isObject(second[prop])) {
        resultantTree[prop] = null;
      } else {
        let subTree = {};
        resultantTree[prop] = subTree;
        unionKeysHelper(first[prop], second[prop], subTree);
      }
    }
  }
}

/**
 * Checks if a value of a JSON property is an 'object'
 * @param {Object} o - a plain JS object
 * @return {boolean}
 */
function isObject(o) {
  return typeof o === 'object' && !Array.isArray(o) && o !== null;
}
