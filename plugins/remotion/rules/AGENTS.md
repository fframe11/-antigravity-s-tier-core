# Remotion Video Engineering Rules

## 1. Frame-Driven Deterministic Rendering
- Every visual property MUST be derived from `useCurrentFrame()`.
- Never use non-deterministic sources: `Date.now()`, `Math.random()`, `setTimeout`, or `setInterval`.
- CSS keyframes/transitions and Tailwind animation classes are STRICTLY FORBIDDEN (they do not render correctly in headless frames).

## 2. Animation & Interpolation
- Animate properties using `useCurrentFrame()` and `interpolate()`.
- Always clamp interpolated values: `{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }`.
- When animating `scale`, use `{ output: 'perceptual-scale' }` for natural easing.
- Keep units consistent across `outputRange` (all `px`, all `deg`, all numbers).

## 3. Assets & Media
- Place static assets in `public/` and load via `staticFile("asset.png")`.
- Render images with `<Img src={staticFile("...")} />`.
- Render videos with `<Video src={staticFile("...")} />` from `@remotion/media`.
- Render audio with `<Audio src={staticFile("...")} />`.

## 4. Timelines & Sequences
- Use `<Sequence from={startFrame} durationInFrames={length}>` for scene management and time-shifting.
- Remember `useCurrentFrame()` inside a `<Sequence>` is relative to that sequence's start frame.
