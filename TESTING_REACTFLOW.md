# Testing the ReactFlow Workflow Implementation

## Quick Start

### 1. Start the Development Server

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:3000`

### 2. Test the Basic Flow

1. **Navigate to Generate Page**
   - Go to `http://localhost:3000/generate`
   - You should see the ReactFlow canvas with a gradient background
   - The Topic node should be visible and expanded

2. **Complete Topic Step**
   - Enter a topic (e.g., "Artificial Intelligence")
   - Select a format (Single Host or Two Hosts)
   - Click "Continue to References"
   - ✅ Node should collapse and show a green checkmark
   - ✅ References node should fade in and expand

3. **Complete References Step**
   - Wait for videos to load (should see loading spinner)
   - Select 1-5 videos by clicking them
   - Click "Continue to Analysis"
   - ✅ Node should collapse with summary showing count
   - ✅ Outline node should appear

4. **Complete Outline Step**
   - Wait for analysis to complete (3 stages: transcripts → analysis → outline)
   - Review the generated outline
   - Click "Generate Script"
   - ✅ Script node appears

5. **Complete Script Step**
   - Wait for script generation
   - Review the script preview
   - Click "Generate Audio"
   - ✅ Audio node appears

6. **Complete Audio Step**
   - Wait for audio generation
   - ✅ Confetti animation plays
   - Test play/pause buttons
   - Test download button

## Test Cases

### ✅ Core Functionality

#### Node Expansion/Collapse
- [ ] Click collapsed node to expand
- [ ] Click X button to collapse
- [ ] Press ESC to collapse active node
- [ ] Only one node expanded at a time

#### Sequential Flow
- [ ] Nodes appear in order (no skipping)
- [ ] Previous nodes collapse before next appears
- [ ] Edges connect nodes correctly
- [ ] Edge colors change: blue (active) → green (completed)

#### Edit Mode
- [ ] Click completed Topic node
- [ ] Node expands and becomes editable
- [ ] All future nodes disappear
- [ ] Edit mode banner appears at top
- [ ] Make changes and continue
- [ ] Workflow rebuilds from edited point

#### Loading States
- [ ] Pulsing border during API calls
- [ ] Loading spinner in node content
- [ ] Stage indicators (e.g., "Analyzing content...")
- [ ] Loading doesn't block other interactions

#### Error Handling
- [ ] Simulate API failure (disconnect internet)
- [ ] Error message displays in node
- [ ] Retry button appears
- [ ] Error doesn't crash entire workflow
- [ ] Other nodes remain functional

### ✅ Visual & Animation

#### Node Animations
- [ ] New nodes fade in with scale animation
- [ ] Expansion is smooth (no jank)
- [ ] Completion checkmark appears
- [ ] Hover effects on collapsed nodes

#### Edge Animations
- [ ] Edges draw smoothly when node added
- [ ] Active edges show animated dots
- [ ] Completed edges turn green
- [ ] Edge labels show data summary

#### Confetti Effect
- [ ] Plays only when audio completes
- [ ] Particles fall and rotate
- [ ] Doesn't interfere with interactions
- [ ] Clears after 3 seconds

### ✅ Responsive Design

#### Desktop (>1024px)
- [ ] All nodes fit on screen with default zoom
- [ ] MiniMap visible in bottom-right
- [ ] Controls visible in bottom-left
- [ ] Header and progress panels visible

#### Tablet (768px - 1024px)
- [ ] Nodes scale appropriately
- [ ] Pan/zoom works smoothly
- [ ] Touch gestures work (if touch device)
- [ ] MiniMap hidden

#### Mobile (<768px)
- [ ] Canvas fills screen
- [ ] Touch pan/zoom works
- [ ] Nodes readable at default zoom
- [ ] Controls accessible
- [ ] MiniMap hidden

### ✅ Keyboard Shortcuts

- [ ] ESC: Collapse expanded node
- [ ] Arrow keys: Pan canvas (when not in input)
- [ ] +/-: Zoom in/out (via controls)
- [ ] Space + drag: Pan canvas

### ✅ Accessibility

- [ ] Tab navigation works
- [ ] Focus visible on interactive elements
- [ ] Screen reader announces node states
- [ ] Error messages readable
- [ ] Color contrast passes WCAG AA

## Browser Testing

Test in multiple browsers:

- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest)
- [ ] **Edge** (latest)
- [ ] **Mobile Safari** (iOS)
- [ ] **Mobile Chrome** (Android)

## Performance Testing

### Load Times
- [ ] Initial page load < 2s
- [ ] Node expansion instant (< 100ms)
- [ ] Canvas interactions smooth (60fps)
- [ ] No memory leaks after extended use

### Network Conditions
- [ ] Works on fast 3G
- [ ] Handles API timeouts gracefully
- [ ] Retry logic works
- [ ] Loading states clear

## Edge Cases

### Data Validation
- [ ] Empty topic input disabled
- [ ] No videos selected disabled
- [ ] API errors handled
- [ ] Malformed responses caught

### User Behavior
- [ ] Multiple rapid clicks on buttons (debounced)
- [ ] Navigate away during API call
- [ ] Refresh page during workflow
- [ ] Back button behavior
- [ ] Forward button behavior

### State Management
- [ ] Edit mode clears future data
- [ ] Node data persists on collapse
- [ ] Callbacks maintain correct scope
- [ ] No stale closure issues

## Known Limitations

1. **No Persistence**: Refreshing page loses progress
   - Future: Add localStorage/sessionStorage
   
2. **No Undo/Redo**: Can't undo node completion
   - Future: Implement command pattern

3. **Single User**: No real-time collaboration
   - Future: Add WebSocket sync

4. **No Validation**: Can edit completed nodes without warning
   - Future: Add confirmation dialog

## Debugging Tips

### React DevTools
```bash
# Install React DevTools browser extension
# Inspect component tree and props
```

### ReactFlow DevTools
```javascript
// Add to page.tsx for debugging
import { useReactFlow } from 'reactflow';

const { getNodes, getEdges } = useReactFlow();
console.log('Nodes:', getNodes());
console.log('Edges:', getEdges());
```

### Common Issues

**Issue**: Nodes don't appear
- Check console for errors
- Verify node types registered
- Check state updates

**Issue**: Edges not connecting
- Verify source/target IDs match node IDs
- Check Handle components present
- Verify edge array updated

**Issue**: Animations not working
- Check CSS loaded (globals.css)
- Verify animation classes applied
- Check browser supports CSS animations

**Issue**: Touch not working on mobile
- Verify `panOnDrag` and `zoomOnPinch` props set
- Check touch-action CSS not blocking
- Test on actual device (simulators may differ)

## Success Criteria

The implementation is successful if:

✅ All 12 test cases pass
✅ No console errors during normal flow
✅ Build completes without warnings
✅ TypeScript types all resolve
✅ Animations smooth (60fps)
✅ Mobile experience functional
✅ Edit mode works correctly
✅ Error recovery functional

## Reporting Issues

If you find bugs, please note:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser and device
4. Console error messages
5. Screenshots/video if possible

---

Happy Testing! 🎉

