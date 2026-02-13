-- Convert TeX page break directives to EPUB-compatible HTML page breaks.
local PAGEBREAK_HTML = '<p style="page-break-after: always;"> </p>'

function RawBlock(el)
  if el.format == 'tex' and el.text:match('^\\newpage%s*$') then
    return pandoc.RawBlock('html', PAGEBREAK_HTML)
  end
  return nil
end
