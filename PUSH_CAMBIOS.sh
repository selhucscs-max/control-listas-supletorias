#!/bin/bash
# Script para subir los cambios a GitHub rápidamente

echo "📤 Subiendo cambios a GitHub..."
echo ""

# Verificar que estamos en el repo correcto
if [ ! -d ".git" ]; then
    echo "❌ Error: No estamos en un repositorio Git"
    exit 1
fi

# Mostrar cambios pendientes
echo "📝 Cambios pendientes:"
git log --oneline -3

echo ""
echo "🔄 Haciendo push a origin/main..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Cambios subidos correctamente!"
    echo ""
    echo "🔗 Ver en GitHub:"
    git config --get remote.origin.url | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/.git$//'
    echo ""
    echo "📅 Los eventos se sincronizarán automáticamente cuando hagas push a CONTROL_SUPLES.ods"
else
    echo ""
    echo "❌ Error al subir cambios"
    echo "Asegúrate de que tienes acceso al repositorio"
    exit 1
fi
