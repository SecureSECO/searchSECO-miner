import * as fs from 'fs';

interface Person {
  '@type': string;
  name: string;
  affiliation?: string;
  identifier?: {
    '@type': string;
    propertyID: string;
    value: string;
  };
}

interface CodeMeta {
  name?: string;
  description?: string;
  version?: string;
  url?: string;
  license?: string;
  author?: Person[];
  keywords?: string[];
  repository?: string;
  referencePublication?: {
    '@type': string;
    name: string;
    publisher: string;
    url: string;
  }[];
  identifier?: {
    '@type': string;
    propertyID: string;
    value: string;
  }[];
}

interface CffAuthor {
  'family-names': string;
  'given-names': string;
  'affiliation'?: string;
  'orcid'?: string;
}

interface CffContent {
  'cff-version': string;
  message: string;
  title?: string;
  type: string;
  authors: CffAuthor[];
  version?: string;
  url?: string;
  license?: string;
  doi?: string;  
}

function generateCffFromCodeMeta(codeMetaFile: string, cffFile: string): void {
  // Read code-meta.json
  const codeMetaJson = fs.readFileSync(codeMetaFile, 'utf-8');
  const codeMeta: CodeMeta = JSON.parse(codeMetaJson);

  // Extract DOI from identifiers
  const doi = (codeMeta.identifier || [])
    .find(id => id.propertyID === 'DOI')?.value || '';

  // Map CodeMeta to CFF content
  const cffContent: CffContent = {
    'cff-version': '1.2.0',
    message: 'If you use this software or the associated data, feel free to cite us.',
    title: codeMeta.name,
    type: 'software',
    authors: (codeMeta.author || []).map(person => {
      const nameParts = person.name.split(' ');
      const givenNames = nameParts.slice(0, -1).join(' ');
      const familyNames = nameParts.slice(-1).join(' ');
      return {
        'family-names': familyNames || '',
        'given-names': givenNames || '',
        'affiliation': person.affiliation,
        'orcid': person.identifier?.value
      };
    }),
    version: codeMeta.version,
    url: codeMeta.url,
    license: codeMeta.license,
    doi: doi  
  };

  // Write to CFF file
  fs.writeFileSync(cffFile, `cff-version: ${cffContent['cff-version']}
message: ${cffContent.message}
title: ${cffContent.title || ''}
type: ${cffContent.type}
authors:
${cffContent.authors.map(author => 
  `  - family-names: ${author['family-names']}
    given-names: ${author['given-names']}
    affiliation: ${author['affiliation'] || ''}
    orcid: ${author['orcid'] || ''}`
).join('\n')}
version: ${cffContent.version || ''}
url: ${cffContent.url || ''}
license: ${cffContent.license || ''}
doi: ${cffContent.doi || ''}`);  
}
