/**
 * @fileoverview A utility script that fetches JSON responses and writes the
 * JSON response to a file.
 * @author jbronder
 */

import { writeFile } from 'node:fs/promises';
import { argv, exit } from 'node:process';
import { URL } from 'node:url';

if (argv.length < 7) {
  console.error(`Not enough args.`);
  console.log(`USAGE: node reqScript <standard> <latitude> <longitude> <riskCategory> <siteClass>`);
  exit(1);
}

const BASE_URL = 'https://earthquake.usgs.gov/';
const designStandard = argv[2];
const relativePath = `/ws/designmaps/${designStandard}.json`;

let url = new URL(relativePath, BASE_URL);
console.log(url.toString());

let params = new Map();
params.set('latitude', argv[3]);
params.set('longitude', argv[4]);
params.set('riskCategory', argv[5]);
params.set('siteClass', argv[6]);
params.set('title', 'Example');


let query = new URLSearchParams(params);
console.log(query.toString());
url.search = query;
console.log(url.toString());
try {
  const response = await fetch(url);
  const jsonData = await response.json();
  const jsonStr = JSON.stringify(jsonData);
  await writeFile(`${designStandard}response.json`, jsonStr);
} catch (err) {
  console.error(err);
}

