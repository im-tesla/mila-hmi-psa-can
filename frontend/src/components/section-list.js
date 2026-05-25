import { SECTIONS } from '../can-definitions.js';
import { createSection } from './section.js';

export function createSectionList() {
  const container = document.createElement('div');
  container.id = 'section-list';
  container.className = 'px-4 pb-4';

  const sections = [];

  for (const sectionDef of SECTIONS) {
    const sectionData = createSection(sectionDef);
    container.appendChild(sectionData.element);
    sections.push({ def: sectionDef, element: sectionData.element, highlightSignals: sectionData.highlightSignals });
  }

  return { container, sections };
}
