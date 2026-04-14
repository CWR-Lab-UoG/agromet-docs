# Videos Directory

This directory contains video demonstrations, lectures, and tutorials for the ON1 site documentation.

## Organization

```
videos/
├── tutorials/              # Step-by-step tutorials
│   ├── site-orientation.mp4
│   ├── tga-setup.mp4
│   └── ec-installation.mp4
├── lectures/              # Theory lectures
│   ├── ec-theory.mp4
│   ├── fg-method.mp4
│   └── most-principles.mp4
└── maintenance/          # Maintenance procedures
    ├── sensor-cleaning.mp4
    ├── calibration.mp4
    └── troubleshooting.mp4
```

## File Naming Conventions

Use descriptive, lowercase names:

✓ `tga-daily-checks.mp4`  
✓ `ec-sensor-installation.mp4`  
✓ `theory-eddy-covariance.mp4`  

✗ `VID_20231201.mp4`  
✗ `New Video.MP4`  

## Video Guidelines

### File Formats

- **Preferred**: MP4 (H.264 codec)
- **Alternative**: WebM
- **Avoid**: MOV, AVI (large file sizes)

### File Sizes

- **Target**: < 50MB for short videos (< 10 min)
- **Maximum**: 100MB for longer content
- Consider YouTube for videos > 100MB

### Resolution

- **Minimum**: 720p (1280×720)
- **Recommended**: 1080p (1920×1080)
- **Maximum**: 1080p (no need for 4K for documentation)

### Duration

- **Tutorials**: 5-15 minutes each
- **Lectures**: 20-30 minutes maximum
- **Quick tips**: < 5 minutes

## Video Production Tips

### Recording

✓ Use good lighting  
✓ Clear audio (use external mic if possible)  
✓ Stable camera/screen capture  
✓ Plan content beforehand  
✓ Keep it focused on single topic

### Editing

- Remove long pauses and mistakes
- Add title card at beginning
- Include chapter markers for longer videos
- Add captions/subtitles when possible
- Export at consistent quality

### Equipment

- **Phone camera**: Adequate for field work
- **Screen recording**: OBS Studio, QuickTime
- **Editing**: iMovie, DaVinci Resolve (free), Adobe Premiere

## Embedding Videos

### Local Videos (Small Files)

```html
<video width="100%" controls>
  <source src="../videos/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

*Video: Description of the video content*
```

### YouTube Videos (Recommended for Large Files)

```html
<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe 
    src="https://www.youtube.com/embed/VIDEO_ID" 
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    frameborder="0" 
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen>
  </iframe>
</div>

*Video: Description and duration*
```

### Vimeo Videos

```html
<div style="position: relative; padding-bottom: 56.25%; height: 0;">
  <iframe 
    src="https://player.vimeo.com/video/VIDEO_ID" 
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    frameborder="0" 
    allow="autoplay; fullscreen; picture-in-picture" 
    allowfullscreen>
  </iframe>
</div>
```

## Video Compression

### Using FFmpeg (Recommended)

Compress video while maintaining quality:

```bash
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -crf 23 output.mp4
```

Parameters:
- `-crf 23`: Quality (18-28, lower = better quality)
- `-vcodec h264`: Video codec
- `-acodec aac`: Audio codec

Resize video:

```bash
ffmpeg -i input.mp4 -vf scale=1280:720 -crf 23 output.mp4
```

### Online Tools

- **HandBrake**: Free, easy-to-use GUI
- **CloudConvert**: Online converter
- **Adobe Media Encoder**: Professional option

## Required Videos (To Be Added)

### Priority 1 - Essential
- [ ] site-orientation.mp4 (10 min) - Overview of site and safety
- [ ] tga-daily-checks.mp4 (5 min) - Daily TGA monitoring
- [ ] ec-data-quality.mp4 (8 min) - Checking EC data quality

### Priority 2 - Tutorials
- [ ] tga-setup.mp4 (15 min) - Complete TGA setup procedure
- [ ] ec-installation.mp4 (15 min) - EC sensor installation
- [ ] calibration-procedure.mp4 (12 min) - Calibration walkthrough
- [ ] sensor-cleaning.mp4 (8 min) - Cleaning procedures

### Priority 3 - Theory
- [ ] ec-theory.mp4 (25 min) - Eddy covariance fundamentals
- [ ] fg-method.mp4 (25 min) - Flux-gradient method
- [ ] most-principles.mp4 (20 min) - MOST theory
- [ ] footprint-concepts.mp4 (15 min) - Understanding footprints

### Priority 4 - Troubleshooting
- [ ] common-problems.mp4 (15 min) - Common issues and solutions
- [ ] tga-troubleshooting.mp4 (10 min) - TGA-specific issues
- [ ] ec-troubleshooting.mp4 (10 min) - EC-specific issues

## Accessibility

### Captions/Subtitles

Always provide captions for accessibility:

1. **Automatic**: YouTube auto-captions (review for accuracy)
2. **Manual**: Create SRT file
3. **Professional**: Paid transcription services

### Transcripts

Provide full transcripts for all videos:

- Place in `docs/transcripts/`
- Link from video page
- Improves searchability and accessibility

### Audio Description

For videos with important visual content:

- Describe what's being shown
- Mention equipment locations
- Narrate procedural steps

## Video Hosting Options

### Option 1: Local Storage (Small Files)
**Pros**: Full control, fast loading, no ads  
**Cons**: Increases repo size, bandwidth costs

**Best for**: Short clips < 20MB

### Option 2: YouTube
**Pros**: Free hosting, good compression, analytics  
**Cons**: Ads (unless paid), requires Google account

**Best for**: Longer videos, lectures, public content

### Option 3: Vimeo
**Pros**: Professional appearance, no ads on free tier  
**Cons**: Limited storage on free plan

**Best for**: Professional presentations

### Option 4: Institutional Server
**Pros**: University resources, no ads, privacy  
**Cons**: Access restrictions, may require authentication

**Best for**: Restricted or internal content

## Maintenance Checklist

### Monthly
- [ ] Check all video links are working
- [ ] Review YouTube analytics (if applicable)
- [ ] Update video descriptions if needed

### Quarterly
- [ ] Review content accuracy
- [ ] Update outdated procedures
- [ ] Consider new video topics based on user feedback

### Annually
- [ ] Comprehensive review of all videos
- [ ] Re-record outdated content
- [ ] Assess video effectiveness

## Best Practices

1. **Keep it short**: Break long topics into multiple short videos
2. **Be clear**: Speak clearly and at moderate pace
3. **Show and tell**: Demonstrate while explaining
4. **Use chapters**: Add timestamps for different sections
5. **Quality audio**: Good audio > good video
6. **Test playback**: Verify on different devices
7. **Update regularly**: Keep content current

## Resources

### Free Video Tools
- **OBS Studio**: Screen recording
- **DaVinci Resolve**: Professional editing (free)
- **HandBrake**: Video compression
- **FFmpeg**: Command-line processing
- **Audacity**: Audio editing

### Tutorials
- [OBS Studio Guide](https://obsproject.com/wiki/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [YouTube Creator Academy](https://creatoracademy.youtube.com/)

---

Last updated: December 2025
