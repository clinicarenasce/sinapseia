import os
import re


def extrair_wikilinks(conteudo):
    """Returns all [[wikilink]] target names from markdown content."""
    # Handles [[Link]], [[Link|Alias]], [[Link#heading]]
    return re.findall(r'\[\[([^\]|#\n]+?)(?:[|#][^\]]+)?\]\]', conteudo)


def criar_stubs_wikilinks(conteudo, vault_path):
    """Creates minimal stub .md files for [[wikilinks]] that don't exist yet.

    Returns list of (nome, path) tuples for every stub created.
    Skips: dates, single chars, names with path separators, and existing files.
    """
    if not vault_path or not os.path.isdir(vault_path):
        return []

    links = set(l.strip() for l in extrair_wikilinks(conteudo) if l.strip())
    criados = []

    for nome in links:
        # Skip obvious non-page links: dates, very short names, paths
        if len(nome) <= 2:
            continue
        if re.match(r'^\d{4}-\d{2}-\d{2}$', nome):  # ISO date
            continue
        if re.match(r'^\d+$', nome):  # pure numbers
            continue
        if '/' in nome or '\\' in nome:
            continue

        path = os.path.join(vault_path, f"{nome}.md")
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# {nome}\n\n")
                criados.append((nome, path))
            except Exception:
                pass

    return criados


def ler_tags_vault(vault_path, max_arquivos=60):
    """Reads existing tags from YAML frontmatter of .md files in a vault/graph.

    Returns a deduplicated sorted list of up to 50 tags.
    """
    if not vault_path or not os.path.isdir(vault_path):
        return []

    tags = set()
    count = 0
    try:
        for arquivo in os.listdir(vault_path):
            if not arquivo.endswith(".md"):
                continue
            count += 1
            if count > max_arquivos:
                break
            try:
                path = os.path.join(vault_path, arquivo)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    cabecalho = f.read(1500)

                # tags: [tag1, tag2, tag3]
                m = re.search(r'^tags:\s*\[([^\]]+)\]', cabecalho, re.MULTILINE)
                if m:
                    for t in m.group(1).split(","):
                        t = t.strip().strip("'\"")
                        if t:
                            tags.add(t)
                    continue

                # tags:\n  - tag1\n  - tag2
                m = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', cabecalho, re.MULTILINE)
                if m:
                    for t in re.findall(r'-\s*(.+)', m.group(1)):
                        t = t.strip().strip("'\"")
                        if t:
                            tags.add(t)
            except Exception:
                pass
    except Exception:
        pass

    return sorted(tags)[:50]
