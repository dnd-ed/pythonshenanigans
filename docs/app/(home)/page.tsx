import Link from 'next/link';
import {
  appDescription,
  appName,
  fullLogo,
  githubUrl,
  pypiUrl,
} from '@/lib/shared';

const features = [
  {
    title: 'Build movesets',
    body: 'Compose skills from typed node builders — hitboxes, projectiles, visuals, particles, branches and more.',
  },
  {
    title: 'Load and edit',
    body: 'Decode a code the game produced, change it, and export it again without losing a single field.',
  },
  {
    title: 'Inspect anything',
    body: 'Summarise a code or dump its whole node graph as readable JSON when you need to see what it does.',
  },
];

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col items-center px-6 py-16">
      <img
        src={fullLogo}
        alt={appName}
        className="w-full max-w-3xl px-4"
        // the wordmark is the heading on this page
      />

      <p className="mt-8 max-w-xl text-center text-lg text-fd-muted-foreground">
        {appDescription}
      </p>

      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/docs"
          className="rounded-lg bg-fd-primary px-5 py-2.5 font-medium text-fd-primary-foreground transition-opacity hover:opacity-90"
        >
          Read the docs
        </Link>
        <Link
          href="/docs/getting-started/installation"
          className="rounded-lg border px-5 py-2.5 font-medium transition-colors hover:bg-fd-accent"
        >
          Install
        </Link>
        <a
          href={githubUrl}
          className="rounded-lg border px-5 py-2.5 font-medium transition-colors hover:bg-fd-accent"
        >
          GitHub
        </a>
        <a
          href={pypiUrl}
          className="rounded-lg border px-5 py-2.5 font-medium transition-colors hover:bg-fd-accent"
        >
          PyPI
        </a>
      </div>

      <pre className="mt-8 rounded-lg border bg-fd-card px-4 py-2 font-mono text-sm">
        pip install pythonshenanigans
      </pre>

      <div className="mt-16 grid max-w-4xl gap-4 sm:grid-cols-3">
        {features.map((feature) => (
          <div key={feature.title} className="rounded-xl border bg-fd-card p-5">
            <h2 className="font-semibold">{feature.title}</h2>
            <p className="mt-2 text-sm text-fd-muted-foreground">{feature.body}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
