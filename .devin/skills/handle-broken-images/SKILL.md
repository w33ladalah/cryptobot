# Handle Broken Images in React/Next.js Components

When adding Image components that display user-generated or fetched content, always add error handlers to hide the entire container (including tooltips) when the image fails to load.

## Pattern

### For Link-wrapped images (with Tooltips)

When an Image is wrapped in a Link component inside a Tooltip, hide the Link element:

```tsx
<Image
  src={imageUrl}
  alt="Description"
  width={64}
  height={64}
  className="w-full h-full object-cover"
  unoptimized={true}
  onError={(e) => {
    const link = (e.target as HTMLElement).closest('a') as HTMLElement;
    if (link) {
      link.style.display = 'none';
    }
  }}
/>
```

### For group-wrapped images (without Link)

When an Image is wrapped in a div with class "group" (not inside a Link), hide the group container:

```tsx
<Image
  src={imageUrl}
  alt="Description"
  width={64}
  height={64}
  className="w-full h-full object-cover"
  unoptimized={true}
  onError={(e) => {
    const container = (e.target as HTMLElement).closest('.group') as HTMLElement;
    if (container) {
      container.style.display = 'none';
    }
  }}
/>
```

## Key Points

- **Type casting**: Use `(e.target as HTMLElement)` to access DOM properties
- **Null check**: Always check if the element exists before setting `display = 'none'`
- **Selector choice**: 
  - Use `closest('a')` for Link-wrapped images (hides entire clickable area + tooltip)
  - Use `closest('.group')` for group-wrapped images (hides container div)
- **Why**: Hiding just the `<img>` tag leaves empty containers visible; hiding the parent container provides cleaner UX

## When to Apply

Apply this pattern to:
- Sidebar image components (latest predictions, favorite images, previous predictions)
- Gallery image displays
- Any user-generated content that might have broken URLs
- Image thumbnails in lists or grids

## Files Updated (Reference)

- `frontend/src/components/sidebar/left/ProductSidebar.tsx`
- `frontend/src/components/sidebar/left/EnhanceSidebar.tsx`
- `frontend/src/components/sidebar/left/VideoSidebar.tsx`
- `frontend/src/components/sidebar/left/OtherSidebar.tsx`
- `frontend/src/components/sidebar/left/EditSidebar.tsx`
- `frontend/src/components/sidebar/left/QuickToolsSidebar.tsx`
- `frontend/src/components/sidebar/left/TalkingVideoSidebar.tsx`
- `frontend/src/components/sidebar/left/ProductResultSidebar.tsx`
- `frontend/src/components/sidebar/left/ComposeSidebar.tsx`
- `admin/src/app/gallery/main/page.tsx`
