/**
 * Scene visual mapping: each scenario gets an accent color, gradient, and
 * optional Unsplash backdrop. Backdrops are loaded with onerror fallback to
 * the gradient so a dead external link never blanks the UI.
 */

// Unsplash source URLs (featured, query-based — stable enough for demo).
// All overlaid at low opacity on top of the gradient.
const U = (q) => `https://images.unsplash.com/${q}?auto=format&fit=crop&w=1200&q=60`

export const SCENES = {
  // Daily Life — warm tones
  coffee_shop: { accent: '#b45309', gradient: ['#fef3c7', '#fde68a'], image: U('photo-1501339847302-ac426a4a7cbb') },
  grocery:     { accent: '#15803d', gradient: ['#dcfce7', '#bbf7d0'], image: U('photo-1542838132-92c53300491e') },
  doctor:      { accent: '#0369a1', gradient: ['#e0f2fe', '#bae6fd'], image: U('photo-1576091160550-2173dba999ef') },
  restaurant:  { accent: '#be123c', gradient: ['#ffe4e6', '#fecdd3'], image: U('photo-1517248135467-4c7edcad34c4') },
  delivery:    { accent: '#c2410c', gradient: ['#ffedd5', '#fed7aa'], image: U('photo-1526367790999-0150786686a2') },

  // Work — cool/professional tones
  interview:   { accent: '#4338ca', gradient: ['#e0e7ff', '#c7d2fe'], image: U('photo-1454165804606-c3d57bc86b40') },
  meeting:     { accent: '#1d4ed8', gradient: ['#dbeafe', '#bfdbfe'], image: U('photo-1517245386807-bb43f82c33c4') },
  coworker:    { accent: '#0f766e', gradient: ['#ccfbf1', '#99f6e4'], image: U('photo-1556761175-5973dc0f32e7') },
  phone_call:  { accent: '#7c3aed', gradient: ['#ede9fe', '#ddd6fe'], image: U('photo-1556656793-08538906a9f8') },
  salary:      { accent: '#a16207', gradient: ['#fef9c3', '#fef08a'], image: U('photo-1554224155-6726b3ff858f') },

  // Travel — sky/ocean tones
  airport:     { accent: '#0e7490', gradient: ['#cffafe', '#a5f3fc'], image: U('photo-1436491865332-7a61a109cc05') },
  hotel:       { accent: '#9333ea', gradient: ['#f3e8ff', '#e9d5ff'], image: U('photo-1566073771259-6a8506099945') },
  directions:  { accent: '#0891b2', gradient: ['#cffafe', '#a5f3fc'], image: U('photo-1473445730015-841f29a9490b') },
  travel:      { accent: '#0d9488', gradient: ['#ccfbf1', '#99f6e4'], image: U('photo-1488646953014-85cb44e25828') },

  // Social — vibrant tones
  smalltalk:   { accent: '#db2777', gradient: ['#fce7f3', '#fbcfe8'], image: U('photo-1543807535-eceef0bc27e1') },
  party:       { accent: '#c026d3', gradient: ['#fae8ff', '#f5d0fe'], image: U('photo-1530103862676-de8c9debad1d') },
  neighbor:    { accent: '#65a30d', gradient: ['#ecfccb', '#d9f99d'], image: U('photo-1448630360428-65456885c650') },
  gym:         { accent: '#dc2626', gradient: ['#fee2e2', '#fecaca'], image: U('photo-1534438327276-14e5300c3a48') },
}

const DEFAULT_SCENE = { accent: '#2563eb', gradient: ['#dbeafe', '#eff6ff'], image: '' }

export function getScene(scenarioId) {
  return SCENES[scenarioId] || DEFAULT_SCENE
}

/** CSS linear-gradient string for a scene. */
export function sceneGradient(scenarioId) {
  const s = getScene(scenarioId)
  return `linear-gradient(135deg, ${s.gradient[0]}, ${s.gradient[1]})`
}
