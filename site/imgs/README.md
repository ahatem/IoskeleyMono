# site/imgs — deployment copies

`assets/` at the repository root is the **canonical** source for every Ioskeley
image. This folder holds copies, not originals.

The duplication is structural, not accidental. `.github/workflows/deploy-pages.yml`
publishes `path: site`, so `site/` becomes the site root. An image referenced as
`../assets/Foo.png` would resolve outside that root and 404 on the published site.
Rather than reference across the root or restructure the deployment, the workflow
copies `assets/*.png` into this directory before uploading:

```yaml
- name: Sync artwork into site
  run: cp assets/*.png site/imgs/

- name: Upload site folder as Pages artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: site
```

The copies are still committed so that opening `site/index.html` from a local
checkout renders correctly without running the workflow.

**Do not edit images here.** Regenerate them in `artwork/` and commit the result to
`assets/`; the next deploy overwrites this folder. If an image here and its
counterpart in `assets/` ever differ byte-for-byte in a way that is not explained
by the documented inter-session text-antialiasing variance, the copy in this
folder is stale.

Files:

| File | Canonical source |
|---|---|
| `SocialPreview.png` / `-Light.png` | `assets/SocialPreview.png` / `-Light.png` |
| `Origins-01-Character-Forms.png` / `-Light.png` | `assets/Origins-01-Character-Forms.png` / `-Light.png` |
| `Origins-02-Overlay-Study.png` / `-Light.png` | `assets/Origins-02-Overlay-Study.png` / `-Light.png` |
| `Origins-03-Code-Texture.png` / `-Light.png` | `assets/Origins-03-Code-Texture.png` / `-Light.png` |