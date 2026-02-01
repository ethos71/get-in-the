#!/bin/bash
# Docker Helper Script - Simplify common Docker operations

set -e

COMPOSE_FILE="docker/docker-compose.yml"

show_help() {
    cat << EOF
Kitchen Layout Generator - Docker Helper

Usage: docker/run.sh [COMMAND] [OPTIONS]

Commands:
    build               Build the Docker image
    kitchen             Generate both SVG and ASCII layouts (recommended)
    milestone           Generate layouts and commit milestone to git
    svg [scale]         Generate SVG layout only (default scale: 3.0)
    ascii [--zoom N]    Generate ASCII layout only
    validate            Validate configuration
    shell               Open interactive shell
    clean               Remove containers and images
    help                Show this help message

Examples:
    docker/run.sh build
    docker/run.sh kitchen
    docker/run.sh milestone "Added door to E2"
    docker/run.sh milestone -t v2.1.0
    docker/run.sh svg 5.0
    docker/run.sh ascii --zoom 1.5
    docker/run.sh validate
    docker/run.sh shell

EOF
}

build_image() {
    echo "🔨 Building Docker image..."
    docker compose -f "$COMPOSE_FILE" build
    echo "✅ Build complete!"
}

generate_kitchen() {
    echo "🏠 Generating kitchen layouts (SVG + ASCII)..."
    docker compose -f "$COMPOSE_FILE" run --rm kitchen-layout python .github/commands/kitchen.py
    echo "✅ Kitchen layouts generated!"
    echo "   📊 SVG:   output/kitchen_layout.svg"
    echo "   📄 ASCII: output/kitchen_layout.txt"
}

create_milestone() {
    echo "🎯 Creating milestone..."
    docker compose -f "$COMPOSE_FILE" run --rm kitchen-layout python .github/commands/milestone.py "$@"
}

generate_svg() {
    local scale="${1:-3.0}"
    echo "🎨 Generating SVG layout (scale: ${scale})..."
    docker compose -f "$COMPOSE_FILE" run --rm kitchen-layout python scripts/engine/svg_renderer.py
    echo "✅ SVG generated at output/kitchen_layout.svg"
}

generate_ascii() {
    echo "📝 Generating ASCII layout..."
    docker compose -f "$COMPOSE_FILE" --profile ascii run --rm ascii-layout
    echo "✅ ASCII layout generated at output/kitchen_layout.txt"
}

validate_config() {
    echo "✔️  Validating configuration..."
    docker compose -f "$COMPOSE_FILE" --profile validate run --rm validate
}

open_shell() {
    echo "🐚 Opening interactive shell..."
    docker compose -f "$COMPOSE_FILE" --profile shell run --rm shell
}

clean() {
    echo "🧹 Cleaning up Docker resources..."
    docker compose -f "$COMPOSE_FILE" down --rmi all -v
    echo "✅ Cleanup complete!"
}

# Main command dispatcher
case "${1:-help}" in
    build)
        build_image
        ;;
    kitchen)
        generate_kitchen
        ;;
    milestone)
        shift
        create_milestone "$@"
        ;;
    svg)
        generate_svg "${2}"
        ;;
    ascii)
        generate_ascii
        ;;
    validate)
        validate_config
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
