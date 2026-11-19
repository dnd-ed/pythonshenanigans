import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
import { appName, fullLogo, githubUrl, smallLogo } from './shared';

/**
 * Landing page: the full wordmark, not the name as text.
 */
export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={fullLogo} alt={appName} className="h-8 w-auto" />
      ),
    },
    githubUrl,
  };
}

/**
 * Inside the docs: the compact "pts" mark next to the name.
 */
export function docsOptions(): BaseLayoutProps {
  return {
    nav: {
      title: (
        <span className="flex items-center gap-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={smallLogo} alt="" className="size-7" />
          <span className="font-semibold">{appName}</span>
        </span>
      ),
    },
    githubUrl,
  };
}
