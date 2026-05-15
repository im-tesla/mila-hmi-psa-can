import { SECTIONS } from '../can-definitions.js';
import { createSection } from './section.js';

export function createSectionList() {
  const container = document.createElement('div');
  container.id = 'section-list';
  container.className = 'px-4 pb-4';

  const sections = [];

  for (const sectionDef of SECTIONS) {
    const { element } = createSection(sectionDef);
    container.appendChild(element);
    sections.push({ def: sectionDef, element });
  }

  return { container, sections };
}
