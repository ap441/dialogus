"use client";

import { useRef, useState } from "react";

import { MarkdownRenderer } from "@/components/MarkdownRenderer";

type Props = {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  rows?: number;
  label?: string;
  hint?: string;
  previewLabel?: string;
  showPreview?: boolean;
};

const toolbar = [
  { label: "Bold", before: "**", after: "**" },
  { label: "Italic", before: "*", after: "*" },
  { label: "Quote", before: "> ", after: "" },
  { label: "Code", before: "`", after: "`" },
  { label: "Link", before: "[", after: "](https://)" },
  { label: "List", before: "- ", after: "" }
];

export function MarkdownEditor({
  value,
  onChange,
  placeholder,
  rows = 6,
  label,
  hint,
  previewLabel = "Preview",
  showPreview = true
}: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  const wrapSelection = (before: string, after: string) => {
    const el = ref.current;
    if (!el) {
      onChange(`${value}${before}${after}`);
      return;
    }

    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    const selected = value.slice(start, end) || (before === "[" ? "link text" : "text");
    const next = `${value.slice(0, start)}${before}${selected}${after}${value.slice(end)}`;
    onChange(next);

    window.requestAnimationFrame(() => {
      const nextStart = start + before.length;
      const nextEnd = nextStart + selected.length;
      el.focus();
      el.setSelectionRange(nextStart, nextEnd);
    });
  };

  return (
    <div className="markdown-editor">
      {label ? <div className="markdown-label">{label}</div> : null}
      <div className="markdown-toolbar">
        {toolbar.map((action) => (
          <button
            key={action.label}
            type="button"
            className="markdown-tool"
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => wrapSelection(action.before, action.after)}
          >
            {action.label}
          </button>
        ))}
        {showPreview ? (
          <button type="button" className="markdown-tool ghost" onClick={() => setPreviewOpen((current) => !current)}>
            {previewOpen ? "Edit" : previewLabel}
          </button>
        ) : null}
      </div>
      <textarea ref={ref} value={value} onChange={(event) => onChange(event.target.value)} rows={rows} placeholder={placeholder} />
      {hint ? <p className="markdown-hint">{hint}</p> : null}
      {showPreview && previewOpen ? (
        <div className="markdown-preview glass">
          <MarkdownRenderer content={value || "*Nothing to preview yet.*"} />
        </div>
      ) : null}
    </div>
  );
}
