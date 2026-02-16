# Graphviz ERD Generation

This directory contains both Mermaid and Graphviz versions of the GHFDB Entity Relationship Diagram.

## Files

- `ghfdb-erd.md` - Original documentation with Mermaid ERD (view in GitHub or VS Code)
- `ghfdb-erd.dot` - Graphviz DOT format ERD (generate images from this)

## Installing Graphviz

### Windows

**Option 1: Automated User Install (No Admin Required - RECOMMENDED)**

Run the provided PowerShell script:

```powershell
cd docs/data_models
.\install_graphviz.ps1
```

This will:
- Download Graphviz portable version
- Extract to `%USERPROFILE%\graphviz`
- Add to your user PATH automatically
- No administrator rights needed

**Option 2: Manual Download with Installer**

1. Visit https://graphviz.org/download/
2. Download the Windows installer (e.g., `graphviz-install-14.1.2-win64.exe`)
3. Run the installer (requires admin rights)
4. Add Graphviz to your PATH:
   - Add `C:\Program Files\Graphviz\bin` to your System Environment Variables
5. Restart your terminal/PowerShell

**Option 3: Using Chocolatey (Requires Admin)**

```powershell
# Run PowerShell as Administrator
choco install graphviz -y
```

**Option 4: Using Scoop**

```powershell
scoop install graphviz
```

### macOS

**Using Homebrew:**
```bash
brew install graphviz
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install graphviz
```

### Verify Installation

```bash
dot -V
```

You should see output like: `dot - graphviz version 14.1.2 (20250126.0804)`

## Generating Diagrams

Once Graphviz is installed, you can generate various output formats:

### PNG (Raster Image)

```bash
cd docs/data_models
dot -Tpng ghfdb-erd.dot -o ghfdb-erd.png
```

### SVG (Vector Image - Recommended for Web)

```bash
dot -Tsvg ghfdb-erd.dot -o ghfdb-erd.svg
```

### PDF (Vector Image - Recommended for Print)

```bash
dot -Tpdf ghfdb-erd.dot -o ghfdb-erd.pdf
```

### High-Resolution PNG

For publication-quality raster images:

```bash
dot -Tpng -Gdpi=300 ghfdb-erd.dot -o ghfdb-erd-300dpi.png
```

## Alternative Layouts

Graphviz supports different layout engines. The default is `dot` (hierarchical), but you can try others:

### Left-to-Right Layout

```bash
dot -Tpng -Grankdir=LR ghfdb-erd.dot -o ghfdb-erd-lr.png
```

### Circular Layout

```bash
circo -Tpng ghfdb-erd.dot -o ghfdb-erd-circo.png
```

### Force-Directed Layout

```bash
neato -Tpng ghfdb-erd.dot -o ghfdb-erd-neato.png
```

## Customization

The DOT file can be edited to customize:

- **Colors**: Modify `BGCOLOR`, `color`, `fontcolor` attributes
- **Layout**: Change `rankdir` (TB, LR, BT, RL)
- **Spacing**: Adjust `nodesep`, `ranksep`, `pad`
- **Fonts**: Change `fontname`, `fontsize`
- **Shapes**: Modify node `shape` attributes

See the [Graphviz documentation](https://graphviz.org/documentation/) for more options.

## Comparison: Mermaid vs Graphviz

| Feature | Mermaid | Graphviz |
|---------|---------|----------|
| **Rendering** | Browser-based, GitHub-integrated | Command-line tool |
| **Quality** | Good for web viewing | Excellent for print/publication |
| **Formats** | SVG (via renderer) | PNG, SVG, PDF, PS, and 20+ more |
| **Editing** | Text-based, simple syntax | Text-based, more verbose |
| **Customization** | Limited styling options | Extensive styling and layout control |
| **Resolution** | Fixed by renderer | Configurable (DPI settings) |
| **Best For** | Documentation, GitHub, web | Publications, presentations, high-quality prints |

## Troubleshooting

### Command Not Found

If you get `dot: command not found`, ensure Graphviz is installed and in your PATH:

**Windows PowerShell:**
```powershell
$env:Path += ";C:\Program Files\Graphviz\bin"
```

**Linux/macOS:**
```bash
export PATH=$PATH:/usr/local/bin
```

### Memory Issues (Large Diagrams)

For very large diagrams, increase memory:

```bash
dot -Gmaxiter=10000 -Gstart=random -Tpng ghfdb-erd.dot -o ghfdb-erd.png
```

### Font Issues

If fonts don't render correctly, try specifying a system font:

```bash
dot -Gfontname="Arial" -Nfontname="Arial" -Efontname="Arial" -Tpng ghfdb-erd.dot -o ghfdb-erd.png
```

## Online Alternatives

If you can't install Graphviz locally, use online renderers:

- **Edotor**: https://edotor.net/
- **Graphviz Online**: https://dreampuf.github.io/GraphvizOnline/
- **Viz.js**: https://viz-js.com/

Simply copy the contents of `ghfdb-erd.dot` and paste into these tools.
