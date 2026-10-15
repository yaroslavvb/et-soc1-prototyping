import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const TAU = Math.PI * 2;
const DEFAULT_VIEW = { yaw: -.68, pitch: .48 };
const DEFAULT_ZOOM = 1.18;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const svgElement = name => document.createElementNS('http://www.w3.org/2000/svg', name);

/**
 * A small, self-contained exhibit viewer. The model supplies a conservative
 * world-space bounding sphere covering every setting of its controls.
 *
 * Regression constraints: orbit NEVER measures projected bounds or changes
 * distance/zoom. Labels occupy named viewport slots; no per-frame collision
 * solver is allowed to relocate their text when the geometry rotates.
 */
export function createViewer({ canvas, overlay, onPick = () => {}, onViewChange = () => {} }) {
  if (!canvas || !overlay) throw new Error('The 3D viewer needs a canvas and label overlay.');

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  // Orbit and carrier motion do not move the shadow-casting structure or key
  // light. Reuse the static map until a model or lighting change invalidates it.
  renderer.shadowMap.autoUpdate = false;
  renderer.shadowMap.needsUpdate = true;
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  // A procedurally lit studio provides broad reflections on metal surfaces.
  // It is compiled into the artifact and needs no image, HDR, or network fetch.
  const environmentRoom = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environmentTarget = pmrem.fromScene(environmentRoom, .04);
  scene.environment = environmentTarget.texture;
  scene.environmentIntensity = 1.05;
  environmentRoom.dispose();
  pmrem.dispose();
  const camera = new THREE.PerspectiveCamera(40, 1, .02, 200);
  const target = new THREE.Vector3();
  const anchorVector = new THREE.Vector3();
  const raycaster = new THREE.Raycaster();
  const pointerNDC = new THREE.Vector2();

  const hemisphere = new THREE.HemisphereLight(0xdbe9ff, 0xb7a493, 1.65);
  const keyLight = new THREE.DirectionalLight(0xfff2df, 3.1);
  const fillLight = new THREE.DirectionalLight(0xadcfff, 1.2);
  const rimLight = new THREE.DirectionalLight(0xe1f4ff, 1.55);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(2048, 2048);
  keyLight.shadow.bias = -.0002;
  keyLight.shadow.normalBias = .035;
  keyLight.shadow.radius = 3;
  scene.add(hemisphere, keyLight, keyLight.target, fillLight, fillLight.target, rimLight, rimLight.target);

  const groundMaterial = new THREE.ShadowMaterial({ color: 0x233846, opacity: .16, depthWrite: false });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  ground.userData.viewerDecoration = true;
  scene.add(ground);

  Object.assign(canvas.style, { display: 'block', width: '100%', height: '100%', touchAction: 'none', cursor: 'grab' });
  if (!canvas.hasAttribute('tabindex')) canvas.tabIndex = 0;
  Object.assign(overlay.style, { position: 'absolute', inset: '0', pointerEvents: 'none', overflow: 'hidden' });
  const leaders = svgElement('svg');
  leaders.setAttribute('aria-hidden', 'true');
  Object.assign(leaders.style, { position: 'absolute', inset: '0', width: '100%', height: '100%', overflow: 'hidden', pointerEvents: 'none' });
  overlay.append(leaders);

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let model = null;
  let radius = 1;
  let distance = 4;
  let width = 1;
  let height = 1;
  let dpr = 1;
  let dark = false;
  let yaw = DEFAULT_VIEW.yaw;
  let pitch = DEFAULT_VIEW.pitch;
  let zoom = DEFAULT_ZOOM;
  let view = 'perspective';
  let auto = false;
  let paused = reducedMotion.matches;
  let selected = '';
  let time = 0;
  let lastTime = null;
  let frameId = 0;
  let disposed = false;
  let labelRows = [];
  let selectionLines = [];
  let pointers = new Map();
  let gesture = null;
  let pinchDistance = 0;

  const reportView = () => onViewChange({ view, auto, zoom, yaw, pitch });
  const shouldAnimate = () => auto || (!paused && typeof model?.update === 'function');

  function schedule() {
    if (!disposed && !document.hidden && !frameId) frameId = requestAnimationFrame(frame);
  }

  function frame(now) {
    frameId = 0;
    if (disposed || document.hidden) { lastTime = null; return; }
    const elapsed = lastTime === null ? 0 : clamp((now - lastTime) / 1000, 0, .05);
    lastTime = now;
    if (!paused) time += elapsed;
    if (auto) yaw = (yaw + elapsed * .15) % TAU;
    draw();
    if (shouldAnimate()) schedule();
    else lastTime = null;
  }

  function placeCamera() {
    // The distance is a scene constant. Rotation changes only the two angles.
    camera.position.set(
      target.x + Math.sin(yaw) * Math.cos(pitch) * distance,
      target.y + Math.sin(pitch) * distance,
      target.z + Math.cos(yaw) * Math.cos(pitch) * distance
    );
    camera.lookAt(target);
    camera.updateMatrixWorld();
  }

  function updateProjection() {
    // Reserve room for fixed callouts. Aspect changes adjust projection once;
    // neither camera angle nor a model control ever enters this calculation.
    // The default view is closer, with a viewport-only cap that keeps even the
    // full bounding sphere inside a narrow phone at the initial/reset zoom.
    const room = Math.max(40, Math.min(width - 42, height - 132, (Math.min(width, height) - 16) / DEFAULT_ZOOM)) / 2;
    const focal = room * Math.sqrt(distance * distance - radius * radius) / radius;
    camera.aspect = width / height;
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(height / (2 * focal)));
    camera.zoom = zoom;
    camera.near = Math.max(.01, radius * .015);
    camera.far = distance + radius * 16;
    camera.updateProjectionMatrix();
  }

  function resize() {
    if (disposed) return;
    const rect = canvas.getBoundingClientRect();
    const nextWidth = Math.max(1, rect.width);
    const nextHeight = Math.max(1, rect.height);
    const nextDPR = Math.min(2, window.devicePixelRatio || 1);
    if (nextWidth === width && nextHeight === height && nextDPR === dpr) return;
    width = nextWidth;
    height = nextHeight;
    dpr = nextDPR;
    renderer.setPixelRatio(dpr);
    renderer.setSize(width, height, false);
    leaders.setAttribute('viewBox', `0 0 ${width} ${height}`);
    updateProjection();
    layoutLabels();
    schedule();
  }

  function styleLabel(row) {
    const active = row.anchor.key === selected;
    row.label.style.color = active ? (dark ? '#96f3de' : '#096f67') : (dark ? '#dbe7ee' : '#43566b');
    row.label.style.background = dark ? 'rgba(22,35,48,.95)' : 'rgba(255,255,255,.95)';
    row.label.style.borderColor = active ? (dark ? '#50baa7' : '#5b9e94') : (dark ? '#445565' : '#cad6dd');
    row.label.style.boxShadow = dark ? '0 2px 10px #0003' : '0 2px 8px #2543580b';
    const color = active ? (dark ? '#96f3de' : '#168d7c') : (dark ? '#8aabb9' : '#738c9a');
    row.path.setAttribute('stroke', color);
    row.dot.setAttribute('fill', color);
  }

  function makeLabels() {
    for (const row of labelRows) row.label.remove();
    leaders.replaceChildren();
    labelRows = (model?.anchors || []).map(anchor => {
      const path = svgElement('path');
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke-width', '1');
      path.setAttribute('stroke-opacity', '.7');
      path.setAttribute('vector-effect', 'non-scaling-stroke');
      const dot = svgElement('circle');
      dot.setAttribute('r', '2.2');
      leaders.append(path, dot);
      const label = document.createElement('span');
      label.textContent = anchor.text;
      label.dataset.part = anchor.key;
      Object.assign(label.style, {
        position: 'absolute', margin: '0', minHeight: '0', height: 'auto',
        padding: '5px 9px', border: '1px solid', borderRadius: '7px',
        font: '550 11px/1.25 "Avenir Next", Avenir, system-ui, sans-serif',
        letterSpacing: '.005em', whiteSpace: 'nowrap', overflow: 'hidden',
        textOverflow: 'ellipsis', pointerEvents: 'none', userSelect: 'none',
        transition: 'background-color .15s, border-color .15s, color .15s'
      });
      overlay.append(label);
      const row = { anchor, path, dot, label, rect: { x: 0, y: 0, width: 1, height: 1 }, projected: [0, 0] };
      styleLabel(row);
      return row;
    });
    layoutLabels();
  }

  function layoutLabels() {
    const counts = { top: 0, left: 0, right: 0, bottom: 0 };
    for (const row of labelRows) {
      const slot = row.anchor.slot in counts ? row.anchor.slot : 'bottom';
      const index = counts[slot]++;
      row.label.style.fontSize = width < 420 ? '10px' : '11px';
      row.label.style.maxWidth = `${Math.min(160, (width - 40) / 2)}px`;
      const labelWidth = row.label.offsetWidth;
      const labelHeight = row.label.offsetHeight;
      let x = (width - labelWidth) / 2;
      let y;
      if (slot === 'top') y = 44 + index * 30;
      if (slot === 'bottom') y = height - (width < 500 ? 106 : 80) - index * 30;
      if (slot === 'left' || slot === 'right') {
        x = slot === 'left' ? 13 : width - labelWidth - 13;
        y = height - (width < 500 ? 145 : 120) - index * 32;
      }
      row.rect = { x, y, width: labelWidth, height: labelHeight };
      row.label.style.left = `${x}px`;
      row.label.style.top = `${y}px`;
    }
  }

  function updateLeaders() {
    for (const row of labelRows) {
      anchorVector.fromArray(row.anchor.position).project(camera);
      const x = (anchorVector.x * .5 + .5) * width;
      const y = (-anchorVector.y * .5 + .5) * height;
      row.projected = [x, y];
      const visible = anchorVector.z > -1 && anchorVector.z < 1 && Number.isFinite(x + y);
      row.path.style.display = row.dot.style.display = visible ? '' : 'none';
      if (!visible) continue;
      const box = row.rect;
      const centerX = box.x + box.width / 2;
      const centerY = box.y + box.height / 2;
      const dx = x - centerX;
      const dy = y - centerY;
      const fraction = Math.min(box.width / 2 / Math.max(.001, Math.abs(dx)), box.height / 2 / Math.max(.001, Math.abs(dy)), 1);
      row.path.setAttribute('d', `M${centerX + dx * fraction},${centerY + dy * fraction} L${x},${y}`);
      row.dot.setAttribute('cx', String(x));
      row.dot.setAttribute('cy', String(y));
    }
  }

  function partFor(object) {
    for (let node = object; node && node !== scene; node = node.parent) {
      if (node.userData.viewerDecoration) return null;
      if (typeof node.userData.part === 'string') return node.userData.part;
    }
    return null;
  }

  function clearSelection() {
    for (const line of selectionLines) {
      line.removeFromParent();
      line.geometry.dispose();
      line.material.dispose();
    }
    selectionLines = [];
  }

  function applySelection() {
    clearSelection();
    if (!model || !selected) return;
    const meshes = [];
    model.group.traverse(object => {
      if (object.isMesh && object.visible && partFor(object) === selected) meshes.push(object);
    });
    for (const mesh of meshes) {
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(mesh.geometry, 35),
        new THREE.LineBasicMaterial({ color: dark ? 0xa8ffdf : 0x056c65, transparent: true, opacity: .6, depthWrite: false })
      );
      edges.userData.viewerDecoration = true;
      edges.renderOrder = 4;
      mesh.add(edges);
      selectionLines.push(edges);
    }
  }

  function setSelected(key) {
    selected = key || '';
    applySelection();
    labelRows.forEach(styleLabel);
    schedule();
  }

  function disposeModel(oldModel) {
    if (!oldModel) return;
    if (oldModel.dispose) { oldModel.dispose(); return; }
    const geometries = new Set();
    const materials = new Set();
    const textures = new Set();
    oldModel.group.traverse(object => {
      if (object.geometry) geometries.add(object.geometry);
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        if (!material) continue;
        materials.add(material);
        for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
      }
    });
    geometries.forEach(geometry => geometry.dispose());
    materials.forEach(material => material.dispose());
    textures.forEach(texture => texture.dispose());
  }

  function setModel(nextModel) {
    if (!nextModel?.group || !nextModel.bounds?.center || !(nextModel.bounds.radius > 0)) {
      throw new Error('The 3D model needs a group and a fixed bounding sphere.');
    }
    clearSelection();
    if (model && model !== nextModel) { scene.remove(model.group); disposeModel(model); }
    model = nextModel;
    scene.add(model.group);
    target.fromArray(model.bounds.center);
    radius = model.bounds.radius;
    distance = radius * 4;
    ground.position.set(target.x, model.bounds.groundY ?? target.y - radius * .9, target.z);
    ground.scale.set(radius * 4, radius * 4, 1);
    keyLight.position.copy(target).add(new THREE.Vector3(-radius * 2, radius * 4, radius * 3));
    fillLight.position.copy(target).add(new THREE.Vector3(radius * 3, radius * 1.5, -radius));
    rimLight.position.copy(target).add(new THREE.Vector3(radius, radius * 2, -radius * 3));
    for (const light of [keyLight, fillLight, rimLight]) { light.target.position.copy(target); light.target.updateMatrixWorld(); }
    Object.assign(keyLight.shadow.camera, { left: -radius * 1.6, right: radius * 1.6, top: radius * 1.6, bottom: -radius * 1.6, near: .01, far: radius * 12 });
    keyLight.shadow.camera.updateProjectionMatrix();
    renderer.shadowMap.needsUpdate = true;
    updateProjection();
    makeLabels();
    applySelection();
    render();
  }

  function setTheme(value) {
    dark = Boolean(value);
    hemisphere.intensity = dark ? 1.9 : 1.65;
    hemisphere.color.setHex(dark ? 0xbddaff : 0xdbe9ff);
    hemisphere.groundColor.setHex(dark ? 0x526776 : 0xb7a493);
    groundMaterial.color.setHex(dark ? 0x000000 : 0x233846);
    groundMaterial.opacity = dark ? .28 : .16;
    renderer.toneMappingExposure = dark ? 1.18 : 1.12;
    renderer.shadowMap.needsUpdate = true;
    for (const line of selectionLines) line.material.color.setHex(dark ? 0xa8ffdf : 0x056c65);
    labelRows.forEach(styleLabel);
    schedule();
  }

  function setView(name) {
    auto = false;
    view = name;
    if (name === 'top') { yaw = 0; pitch = 1.5; }
    else if (name === 'end' || name === 'side') { yaw = Math.PI / 2; pitch = .12; }
    else if (name === 'front') { yaw = 0; pitch = .08; }
    else { view = 'perspective'; yaw = DEFAULT_VIEW.yaw; pitch = DEFAULT_VIEW.pitch; }
    reportView();
    schedule();
  }

  function zoomBy(factor) {
    if (!(factor > 0) || !Number.isFinite(factor)) return;
    zoom = clamp(zoom * factor, .55, 2.5);
    updateProjection();
    reportView();
    schedule();
  }

  function reset() {
    zoom = DEFAULT_ZOOM;
    updateProjection();
    setView('perspective');
  }

  function setAuto(value) {
    auto = Boolean(value);
    if (auto) view = 'custom';
    lastTime = null;
    reportView();
    schedule();
  }

  function setPaused(value) {
    paused = Boolean(value);
    lastTime = null;
    schedule();
  }

  function orbit(dx, dy) {
    auto = false;
    view = 'custom';
    yaw = (yaw - dx * .006) % TAU;
    pitch = clamp(pitch + dy * .005, -1.4, 1.5);
    reportView();
    schedule();
  }

  function pick(clientX, clientY) {
    if (!model) return;
    const rect = canvas.getBoundingClientRect();
    pointerNDC.set((clientX - rect.left) / rect.width * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(pointerNDC, camera);
    for (const hit of raycaster.intersectObject(model.group, true)) {
      const part = partFor(hit.object);
      if (part) { setSelected(part); onPick(part); break; }
    }
  }

  function pointerDown(event) {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    canvas.setPointerCapture(event.pointerId);
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 1) gesture = { id: event.pointerId, x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY, moved: false };
    else {
      if (gesture) gesture.moved = true;
      const pair = [...pointers.values()];
      pinchDistance = Math.hypot(pair[0].x - pair[1].x, pair[0].y - pair[1].y);
    }
    canvas.style.cursor = 'grabbing';
    canvas.classList.add('dragging');
  }

  function pointerMove(event) {
    if (!pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size >= 2) {
      const pair = [...pointers.values()];
      const nextDistance = Math.hypot(pair[0].x - pair[1].x, pair[0].y - pair[1].y);
      if (pinchDistance > 4 && nextDistance > 4) zoomBy(nextDistance / pinchDistance);
      pinchDistance = nextDistance;
      return;
    }
    if (!gesture || gesture.id !== event.pointerId) return;
    const dx = event.clientX - gesture.x;
    const dy = event.clientY - gesture.y;
    gesture.x = event.clientX;
    gesture.y = event.clientY;
    if (Math.hypot(event.clientX - gesture.startX, event.clientY - gesture.startY) > 4) gesture.moved = true;
    if (gesture.moved) orbit(dx, dy);
  }

  function pointerEnd(event) {
    if (!pointers.has(event.pointerId)) return;
    if (event.type === 'pointerup' && pointers.size === 1 && gesture && !gesture.moved) pick(event.clientX, event.clientY);
    pointers.delete(event.pointerId);
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    pinchDistance = 0;
    if (pointers.size === 1) {
      const [id, point] = pointers.entries().next().value;
      gesture = { id, x: point.x, y: point.y, startX: point.x, startY: point.y, moved: true };
    } else if (!pointers.size) {
      gesture = null;
      canvas.style.cursor = 'grab';
      canvas.classList.remove('dragging');
    }
  }

  function wheel(event) {
    event.preventDefault();
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? height : 1);
    zoomBy(Math.exp(-clamp(delta, -200, 200) * .0015));
  }

  function keyDown(event) {
    // Browser and system shortcuts (Ctrl/Cmd with + or -, Ctrl/Cmd+R, Alt+arrows) stay the browser's.
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    let handled = true;
    switch (event.key) {
      case 'ArrowLeft': orbit(18, 0); break;
      case 'ArrowRight': orbit(-18, 0); break;
      case 'ArrowUp': orbit(0, 18); break;
      case 'ArrowDown': orbit(0, -18); break;
      case '+': case '=': zoomBy(1.12); break;
      case '-': case '_': zoomBy(1 / 1.12); break;
      case 'r': case 'R': case 'Home': reset(); break;
      default: handled = false;
    }
    if (handled) event.preventDefault();
  }

  function visibilityChanged() {
    if (document.hidden) { cancelAnimationFrame(frameId); frameId = 0; }
    else schedule();
    lastTime = null;
  }

  function motionChanged(event) {
    if (event.matches) { paused = true; auto = false; reportView(); schedule(); }
  }

  function draw() {
    if (disposed) return;
    model?.update?.(time);
    placeCamera();
    renderer.render(scene, camera);
    updateLeaders();
  }

  function render() {
    if (disposed) return;
    resize();
    if (!document.hidden) draw();
    if (shouldAnimate()) schedule();
  }

  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  canvas.addEventListener('pointerdown', pointerDown);
  canvas.addEventListener('pointermove', pointerMove);
  canvas.addEventListener('pointerup', pointerEnd);
  canvas.addEventListener('pointercancel', pointerEnd);
  canvas.addEventListener('lostpointercapture', pointerEnd);
  canvas.addEventListener('wheel', wheel, { passive: false });
  canvas.addEventListener('keydown', keyDown);
  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', visibilityChanged);
  reducedMotion.addEventListener('change', motionChanged);

  function dispose() {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frameId);
    resizeObserver.disconnect();
    canvas.removeEventListener('pointerdown', pointerDown);
    canvas.removeEventListener('pointermove', pointerMove);
    canvas.removeEventListener('pointerup', pointerEnd);
    canvas.removeEventListener('pointercancel', pointerEnd);
    canvas.removeEventListener('lostpointercapture', pointerEnd);
    canvas.removeEventListener('wheel', wheel);
    canvas.removeEventListener('keydown', keyDown);
    window.removeEventListener('resize', resize);
    document.removeEventListener('visibilitychange', visibilityChanged);
    reducedMotion.removeEventListener('change', motionChanged);
    clearSelection();
    disposeModel(model);
    ground.geometry.dispose();
    groundMaterial.dispose();
    keyLight.shadow.map?.dispose();
    labelRows.forEach(row => row.label.remove());
    leaders.remove();
    environmentTarget.dispose();
    renderer.dispose();
  }

  function debug() {
    return {
      distance: camera.position.distanceTo(target), baseDistance: distance, zoom: camera.zoom,
      target: target.toArray(), radius, yaw, pitch, view, auto, paused, time,
      width, height, dpr, fov: camera.fov,
      scale: camera.projectionMatrix.elements[5] * height / (2 * distance),
      render: { ...renderer.info.render }, memory: { ...renderer.info.memory },
      labels: labelRows.map(row => ({ key: row.anchor.key, text: row.anchor.text, slot: row.anchor.slot, ...row.rect, anchor: [...row.projected] }))
    };
  }

  resize();
  placeCamera();
  return { setModel, setTheme, setView, zoomBy, reset, setAuto, setPaused, setSelected, render, dispose, debug };
}
