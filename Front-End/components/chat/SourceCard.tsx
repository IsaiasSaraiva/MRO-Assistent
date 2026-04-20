interface SourceCardProps {
  filename: string;
  page?: number;
  excerpt: string;
}

export function SourceCard({ filename, page, excerpt }: SourceCardProps) {
  return (
    <details className="mt-1 rounded-md border-l-2 border-blue-400 bg-muted/50 px-3 py-2 text-xs">
      <summary className="cursor-pointer select-none font-medium">
        <span className="font-semibold">{filename}</span>
        {page != null && <span className="ml-2 text-muted-foreground">p. {page}</span>}
      </summary>
      <p className="mt-2 text-muted-foreground leading-relaxed">{excerpt}</p>
    </details>
  );
}
