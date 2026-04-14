# Images Directory

This directory contains all images used in the documentation.

## Organization

```
images/
├── tower-overview.jpg          # General tower photos
├── ec-sensor.jpg              # EC system photos
├── tga-system.jpg             # TGA system photos
├── site-map.png               # Maps and layouts
├── plots/                     # Data plots and graphs
│   ├── timeseries.png
│   ├── daily-cycle.png
│   └── footprint-map.png
└── diagrams/                  # Schematic diagrams
    ├── tower-schematic.png
    └── sampling-system.png
```

## File Naming Conventions

Use descriptive, lowercase names with hyphens:

✓ `tower-south-view.jpg`  
✓ `ec-sensor-mounting.jpg`  
✓ `data-plot-co2-flux.png`  

✗ `IMG_1234.jpg`  
✗ `Photo1.JPG`  
✗ `new image.png`  

## Image Guidelines

### File Formats

- **Photographs**: Use JPG
- **Diagrams/Charts**: Use PNG
- **Vector graphics**: Consider SVG

### File Sizes

- Keep images under 500KB when possible
- Resize large photos before adding
- Use image optimization tools

### Resolution

- Web display: 1200px width maximum
- Diagrams: 300 DPI for clarity
- Screenshots: Original resolution

### Optimization Tools

- **ImageMagick**: `convert input.jpg -resize 1200x -quality 85 output.jpg`
- **Online tools**: TinyPNG, Squoosh
- **Python**: PIL/Pillow library

## Adding Images to Documentation

### Basic Image

```markdown
![Description](../images/filename.jpg)
```

### Sized Image

```markdown
![Description](../images/filename.jpg){ width="600" }
```

### Aligned Image

```markdown
![Description](../images/filename.jpg){ align=right width="400" }
```

### Image Grid

```markdown
<div class="grid" markdown>
![Image 1](../images/img1.jpg){ width="300" }
![Image 2](../images/img2.jpg){ width="300" }
</div>
```

### Figure with Caption

```markdown
![Tower Setup](../images/tower.jpg){ width="600" }
*Figure 1: ON1 tower showing instrument placement*
```

## Required Images (To Be Added)

### Site Photos
- [ ] tower-overview.jpg - Overall tower view
- [ ] tower-instruments.jpg - Close-up of instruments
- [ ] ec-sensor.jpg - EC sensor detail
- [ ] tga-system.jpg - TGA analyzer
- [ ] site-aerial.jpg - Aerial site view
- [ ] site-map.png - Map showing location

### Equipment Photos
- [ ] irgason.jpg - IRGASON sensor
- [ ] csat3.jpg - CSAT-3 anemometer
- [ ] li7500.jpg - Li-7500 analyzer
- [ ] tga100a.jpg - TGA100A system
- [ ] data-logger.jpg - Data logger setup

### Diagrams
- [ ] tower-schematic.png - Tower height diagram
- [ ] sampling-system.png - TGA sampling schematic
- [ ] ec-concept-diagram.png - EC theory illustration
- [ ] fg-concept-diagram.png - FG theory illustration
- [ ] climate-normals.png - Climate graph

### Data Plots
- [ ] sample-pressure-timeseries.png - Example time series
- [ ] daily-flux-cycle.png - Typical daily patterns
- [ ] footprint-map.png - Flux footprint visualization

## Copyright and Attribution

All images should either be:

1. **Original photos** taken by lab members
2. **Licensed images** with appropriate permissions
3. **Public domain** or Creative Commons images

Always credit external images:

```markdown
![Description](image.jpg)
*Source: [Author/Source name](url) - CC BY 4.0*
```

## Maintenance

- Review image quality quarterly
- Remove unused images
- Update outdated photos
- Compress large files
- Maintain consistent naming

---

Last updated: December 2025
