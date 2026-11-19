import { createGetUrl } from 'fumadocs-core/source';

export const appName = 'PythonShenanigans';
export const appDescription =
  'Build, load and modify Jujutsu Shenanigans movesets from Python.';
export const siteUrl = 'https://pts.itzdanti.dev';

export const docsRoute = '/docs';
export const docsImageRoute = '/og/docs';

export const fullLogo = '/pts_logo.png';
export const smallLogo = '/pts_small_logo.png';

export const gitConfig = {
  user: 'dnd-ed',
  repo: 'pythonshenanigans',
  branch: 'main',
};

export const githubUrl = `https://github.com/${gitConfig.user}/${gitConfig.repo}`;
export const pypiUrl = 'https://pypi.org/project/pythonshenanigans/';

const getImageUrl = createGetUrl(docsImageRoute);

export function getPageImageUrl(page: { slugs: string[]; locale?: string }) {
  const segments = [...page.slugs, 'image.png'];

  return { segments, url: getImageUrl(segments, page.locale) };
}
