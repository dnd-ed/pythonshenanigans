import { Inter } from 'next/font/google';
import type { Metadata } from 'next';
import { Provider } from '@/components/provider';
import { appDescription, appName, siteUrl, smallLogo } from '@/lib/shared';
import './global.css';

const inter = Inter({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${appName} — Jujutsu Shenanigans movesets in Python`,
    template: `%s — ${appName}`,
  },
  description: appDescription,
  applicationName: appName,
  icons: {
    icon: [{ url: smallLogo, type: 'image/png' }],
    shortcut: smallLogo,
    apple: smallLogo,
  },
  openGraph: {
    type: 'website',
    url: siteUrl,
    siteName: appName,
    title: `${appName} — Jujutsu Shenanigans movesets in Python`,
    description: appDescription,
  },
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
