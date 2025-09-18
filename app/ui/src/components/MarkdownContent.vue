<template>
    <div class="markdown-content" v-html="renderedContent"></div>
  </template>
  
  <script setup>
  import { ref, watchEffect } from 'vue';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  
  // Definir props
  const props = defineProps({
    content: {
      type: String,
      required: true
    }
  });
  
  // Referencia reactiva para el contenido renderizado
  const renderedContent = ref('');
  
  // Función para renderizar markdown
  const renderMarkdown = (text) => {
    if (!text) return '';
    
    try {
      // Convertir markdown a HTML usando marked
      const html = marked.parse(text, {
        gfm: true, // GitHub Flavored Markdown
        breaks: true, // Convertir retornos de línea en <br>
        headerIds: true, // Generar IDs para los encabezados
        mangle: false // No codificar caracteres especiales en IDs
      });
      
      // Sanitizar el HTML para prevenir XSS
      const sanitized = DOMPurify.sanitize(html);
      return sanitized;
    } catch (error) {
      console.error('Error rendering markdown:', error);
      return `<p class="text-red-500">Error rendering markdown: ${error.message}</p>`;
    }
  };
  
  // Observar cambios en el contenido y actualizar el HTML renderizado
  watchEffect(() => {
    renderedContent.value = renderMarkdown(props.content);
  });
  </script>
  
  <style scoped>
  .markdown-content {
    color: var(--softtek-primary);
  }
  
  /* Estilos para elementos markdown */
  .markdown-content :deep(h1) {
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
  }
  
  .markdown-content :deep(h2) {
    font-size: 1.5rem;
    font-weight: 600;
    margin-top: 1.25rem;
    margin-bottom: 0.75rem;
  }
  
  .markdown-content :deep(h3) {
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .markdown-content :deep(h4) {
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .markdown-content :deep(p) {
    margin-bottom: 0.75rem;
    line-height: 1.6;
  }
  
  .markdown-content :deep(ul),
  .markdown-content :deep(ol) {
    margin-left: 1.5rem;
    margin-bottom: 1rem;
  }
  
  .markdown-content :deep(ul) {
    list-style-type: disc;
  }
  
  .markdown-content :deep(ol) {
    list-style-type: decimal;
  }
  
  .markdown-content :deep(li) {
    margin-bottom: 0.25rem;
  }
  
  .markdown-content :deep(pre) {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.75rem;
    border-radius: 0.25rem;
    overflow-x: auto;
    margin-bottom: 1rem;
  }
  
  .markdown-content :deep(code) {
    font-family: monospace;
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.15rem 0.3rem;
    border-radius: 0.2rem;
    font-size: 0.9em;
  }
  
  .markdown-content :deep(pre code) {
    background-color: transparent;
    padding: 0;
    border-radius: 0;
  }
  
  .markdown-content :deep(blockquote) {
    border-left: 4px solid var(--fuscia);
    padding-left: 1rem;
    color: rgba(0, 0, 0, 0.7);
    font-style: italic;
    margin-bottom: 1rem;
  }
  
  .markdown-content :deep(a) {
    color: var(--fuscia);
    text-decoration: underline;
  }
  
  .markdown-content :deep(a:hover) {
    color: var(--softtek-primary);
  }
  
  .markdown-content :deep(hr) {
    height: 1px;
    background-color: #e2e8f0;
    border: none;
    margin: 1.5rem 0;
  }
  
  .markdown-content :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
  }
  
  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    border: 1px solid #e2e8f0;
    padding: 0.5rem;
  }
  
  .markdown-content :deep(th) {
    background-color: #f8fafc;
    font-weight: 600;
  }
  
  /* Lista con números en formato plan */
  .markdown-content :deep(ol.plan) {
    counter-reset: plan-counter;
    list-style-type: none;
    margin-left: 0;
    padding-left: 2.5rem;
  }
  
  .markdown-content :deep(ol.plan li) {
    counter-increment: plan-counter;
    position: relative;
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }
  
  .markdown-content :deep(ol.plan li::before) {
    content: counter(plan-counter) ".";
    position: absolute;
    left: -2.5rem;
    width: 2rem;
    text-align: right;
    color: var(--fuscia);
    font-weight: 700;
  }
  </style>