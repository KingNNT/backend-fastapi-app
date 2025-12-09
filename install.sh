#!/bin/bash

# =============================================================================
# FastAPI Backend Template - Remote Installation Script
# =============================================================================
# Install with: curl -fsSL https://raw.githubusercontent.com/KingNNT/backend-fastapi-app/develop/install.sh | bash
# Or: curl -fsSL https://raw.githubusercontent.com/KingNNT/backend-fastapi-app/develop/install.sh | bash -s my-project
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
REPO_URL="https://github.com/KingNNT/backend-fastapi-app.git"
TEMPLATE_NAME="backend-fastapi-app"
TEMPLATE_NAME_SNAKE="backend_fastapi_app"

# -----------------------------------------------------------------------------
# Colors and Formatting
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  FastAPI Backend Template Installer${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Cross-platform sed in-place edit
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Convert kebab-case to snake_case
to_snake_case() {
    echo "$1" | tr '-' '_'
}

# Validate project name (kebab-case, alphanumeric with hyphens)
validate_project_name() {
    if [[ ! "$1" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] && [[ ! "$1" =~ ^[a-z][a-z0-9]*$ ]]; then
        return 1
    fi
    return 0
}

# Validate email format
validate_email() {
    if [[ ! "$1" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 1
    fi
    return 0
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# Main Installation Logic
# -----------------------------------------------------------------------------
main() {
    print_header

    # -------------------------------------------------------------------------
    # Check Prerequisites
    # -------------------------------------------------------------------------
    print_info "Checking prerequisites..."

    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_success "Git is installed"

    if ! command_exists docker; then
        print_warning "Docker is not installed. You'll need it to run the project."
    else
        print_success "Docker is installed"
    fi

    if ! command_exists make; then
        print_warning "Make is not installed. You'll need it to run the project."
    else
        print_success "Make is installed"
    fi

    echo ""

    # -------------------------------------------------------------------------
    # Collect User Input
    # -------------------------------------------------------------------------
    echo -e "${BOLD}${YELLOW}Step 1: Project Configuration${NC}"
    echo ""

    # Check if project name was passed as argument
    if [[ -n "$1" ]]; then
        PROJECT_NAME="$1"
        if ! validate_project_name "$PROJECT_NAME"; then
            print_error "Invalid project name: $PROJECT_NAME"
            print_error "Must be lowercase, start with a letter, use only letters, numbers, and hyphens"
            exit 1
        fi
        print_info "Using project name from argument: $PROJECT_NAME"
    else
        # Interactive prompt for project name
        while true; do
            read -p "$(echo -e "${CYAN}Enter project name ${NC}${BOLD}[kebab-case, e.g., my-awesome-api]${NC}: ")" PROJECT_NAME
            if [[ -z "$PROJECT_NAME" ]]; then
                print_error "Project name cannot be empty"
            elif ! validate_project_name "$PROJECT_NAME"; then
                print_error "Project name must be lowercase, start with a letter, use only letters, numbers, and hyphens"
            elif [[ -d "$PROJECT_NAME" ]]; then
                print_error "Directory '$PROJECT_NAME' already exists"
            else
                break
            fi
        done
    fi

    # Check if directory exists
    if [[ -d "$PROJECT_NAME" ]]; then
        print_error "Directory '$PROJECT_NAME' already exists. Please choose a different name or remove the directory."
        exit 1
    fi

    # Project description
    while true; do
        read -p "$(echo -e "${CYAN}Enter project description${NC}: ")" PROJECT_DESCRIPTION
        if [[ -z "$PROJECT_DESCRIPTION" ]]; then
            print_error "Project description cannot be empty"
        else
            break
        fi
    done

    echo ""
    echo -e "${BOLD}${YELLOW}Step 2: Author Information${NC}"
    echo ""

    # Author name
    while true; do
        read -p "$(echo -e "${CYAN}Enter author name${NC}: ")" AUTHOR_NAME
        if [[ -z "$AUTHOR_NAME" ]]; then
            print_error "Author name cannot be empty"
        else
            break
        fi
    done

    # Author email
    while true; do
        read -p "$(echo -e "${CYAN}Enter author email${NC}: ")" AUTHOR_EMAIL
        if [[ -z "$AUTHOR_EMAIL" ]]; then
            print_error "Author email cannot be empty"
        elif ! validate_email "$AUTHOR_EMAIL"; then
            print_error "Please enter a valid email address"
        else
            break
        fi
    done

    # -------------------------------------------------------------------------
    # Derive Values
    # -------------------------------------------------------------------------
    PROJECT_NAME_SNAKE=$(to_snake_case "$PROJECT_NAME")
    DB_DEV_NAME="${PROJECT_NAME_SNAKE}_dev"
    DB_TEST_NAME="${PROJECT_NAME_SNAKE}_test"
    POSTGRES_DEV_DB="${PROJECT_NAME_SNAKE}_develop"
    POSTGRES_TEST_DB="${PROJECT_NAME_SNAKE}_test"

    # -------------------------------------------------------------------------
    # Confirmation
    # -------------------------------------------------------------------------
    echo ""
    echo -e "${BOLD}${YELLOW}Step 3: Confirmation${NC}"
    echo ""
    echo -e "  ${BOLD}Project name:${NC}         $PROJECT_NAME"
    echo -e "  ${BOLD}Project name (snake):${NC} $PROJECT_NAME_SNAKE"
    echo -e "  ${BOLD}Description:${NC}          $PROJECT_DESCRIPTION"
    echo -e "  ${BOLD}Author:${NC}               $AUTHOR_NAME <$AUTHOR_EMAIL>"
    echo -e "  ${BOLD}Directory:${NC}            ./$PROJECT_NAME"
    echo ""

    read -p "$(echo -e "${YELLOW}Proceed with installation? [Y/n]${NC} ")" CONFIRM
    CONFIRM=${CONFIRM:-Y}
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        print_warning "Installation cancelled"
        exit 0
    fi

    # -------------------------------------------------------------------------
    # Clone Repository
    # -------------------------------------------------------------------------
    echo ""
    echo -e "${BOLD}${YELLOW}Step 4: Cloning Template${NC}"
    echo ""

    print_info "Cloning repository..."
    git clone --depth 1 --branch develop "$REPO_URL" "$PROJECT_NAME" 2>/dev/null
    print_success "Cloned to ./$PROJECT_NAME"

    cd "$PROJECT_NAME"

    # -------------------------------------------------------------------------
    # Update Files
    # -------------------------------------------------------------------------
    echo ""
    echo -e "${BOLD}${YELLOW}Step 5: Customizing Project${NC}"
    echo ""

    # pyproject.toml
    print_info "Updating pyproject.toml..."
    sed_inplace "s/name = \"$TEMPLATE_NAME\"/name = \"$PROJECT_NAME\"/" pyproject.toml
    sed_inplace "s/description = \"Template for backend application use FastAPI\"/description = \"$PROJECT_DESCRIPTION\"/" pyproject.toml
    sed_inplace "s/name = \"kingnnt\"/name = \"$AUTHOR_NAME\"/" pyproject.toml
    sed_inplace "s/email = \"dev.kingnnt@gmail.com\"/email = \"$AUTHOR_EMAIL\"/" pyproject.toml
    print_success "Updated pyproject.toml"

    # Makefile
    print_info "Updating Makefile..."
    sed_inplace "s/PROJECT_NAME := $TEMPLATE_NAME/PROJECT_NAME := $PROJECT_NAME/" Makefile
    print_success "Updated Makefile"

    # makefiles/database.mk
    if [[ -f "makefiles/database.mk" ]]; then
        print_info "Updating makefiles/database.mk..."
        sed_inplace "s/MONGODB_TEST_DATABASE ?= ${TEMPLATE_NAME_SNAKE}_test/MONGODB_TEST_DATABASE ?= $DB_TEST_NAME/" makefiles/database.mk
        print_success "Updated makefiles/database.mk"
    fi

    # .env files
    for env_file in .env .env.example .env.development; do
        if [[ -f "$env_file" ]]; then
            print_info "Updating $env_file..."
            sed_inplace "s/APP_NAME=$TEMPLATE_NAME/APP_NAME=$PROJECT_NAME/" "$env_file"
            sed_inplace "s/APP_DESCRIPTION=Template for backend application use FastAPI/APP_DESCRIPTION=$PROJECT_DESCRIPTION/" "$env_file"
            sed_inplace "s/MONGODB_DATABASE=${TEMPLATE_NAME_SNAKE}_dev/MONGODB_DATABASE=$DB_DEV_NAME/" "$env_file"
            sed_inplace "s/MONGODB_DATABASE=${TEMPLATE_NAME_SNAKE}/MONGODB_DATABASE=$DB_DEV_NAME/" "$env_file"
            sed_inplace "s/MONGODB_TEST_DATABASE=${TEMPLATE_NAME_SNAKE}_test/MONGODB_TEST_DATABASE=$DB_TEST_NAME/" "$env_file"
            sed_inplace "s/POSTGRES_DB=database_develop/POSTGRES_DB=$POSTGRES_DEV_DB/" "$env_file"
            sed_inplace "s/POSTGRES_TEST_DB=database_test/POSTGRES_TEST_DB=$POSTGRES_TEST_DB/" "$env_file"
            print_success "Updated $env_file"
        fi
    done

    # Docker Compose files
    for compose_file in docker-compose.yaml docker-compose.override.yaml docker-compose.production.yaml; do
        if [[ -f "$compose_file" ]]; then
            print_info "Updating $compose_file..."
            sed_inplace "s/$TEMPLATE_NAME/$PROJECT_NAME/g" "$compose_file"
            sed_inplace "s/$TEMPLATE_NAME_SNAKE/$PROJECT_NAME_SNAKE/g" "$compose_file"
            print_success "Updated $compose_file"
        fi
    done

    # Application config files
    if [[ -f "app/infrastructure/configs/app.py" ]]; then
        print_info "Updating app/infrastructure/configs/app.py..."
        sed_inplace "s/default=\"$TEMPLATE_NAME\"/default=\"$PROJECT_NAME\"/" app/infrastructure/configs/app.py
        sed_inplace "s/default=\"Template for backend application use FastAPI\"/default=\"$PROJECT_DESCRIPTION\"/" app/infrastructure/configs/app.py
        sed_inplace "s/default=\"$TEMPLATE_NAME_SNAKE\"/default=\"$PROJECT_NAME_SNAKE\"/" app/infrastructure/configs/app.py
        sed_inplace "s/default=\"${TEMPLATE_NAME_SNAKE}_test\"/default=\"${PROJECT_NAME_SNAKE}_test\"/" app/infrastructure/configs/app.py
        sed_inplace "s/default=\"database_develop\"/default=\"${PROJECT_NAME_SNAKE}_develop\"/" app/infrastructure/configs/app.py
        sed_inplace "s/default=\"database_test\"/default=\"${PROJECT_NAME_SNAKE}_test\"/" app/infrastructure/configs/app.py
        print_success "Updated app/infrastructure/configs/app.py"
    fi

    if [[ -f "app/infrastructure/configs/version.py" ]]; then
        print_info "Updating app/infrastructure/configs/version.py..."
        sed_inplace "s/version(\"$TEMPLATE_NAME\")/version(\"$PROJECT_NAME\")/" app/infrastructure/configs/version.py
        print_success "Updated app/infrastructure/configs/version.py"
    fi

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------
    echo ""
    echo -e "${BOLD}${YELLOW}Step 6: Cleanup${NC}"
    echo ""

    # Remove template git history
    print_info "Removing template git history..."
    rm -rf .git
    print_success "Removed .git directory"

    # Remove install script
    print_info "Removing install script..."
    rm -f install.sh
    print_success "Removed install.sh"

    # Initialize new git repository
    print_info "Initializing new git repository..."
    git init -q
    git add .
    git commit -q -m "Initial commit from FastAPI template"
    print_success "Initialized git repository with initial commit"

    # -------------------------------------------------------------------------
    # Success Message
    # -------------------------------------------------------------------------
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BOLD}Your project is ready at:${NC} ${CYAN}./$PROJECT_NAME${NC}"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo ""
    echo -e "  1. Navigate to your project:"
    echo -e "     ${CYAN}cd $PROJECT_NAME${NC}"
    echo ""
    echo -e "  2. Start development environment:"
    echo -e "     ${CYAN}make dev${NC}"
    echo ""
    echo -e "  3. Access your API:"
    echo -e "     ${CYAN}http://localhost:8080/docs${NC} - Swagger UI"
    echo -e "     ${CYAN}http://localhost:8080/redoc${NC} - ReDoc"
    echo ""
    echo -e "  4. Run tests:"
    echo -e "     ${CYAN}make test${NC}"
    echo ""
    echo -e "${BOLD}Happy coding!${NC}"
    echo ""
}

# Run main with stdin from /dev/tty if piped, otherwise run normally
# This MUST be at the very end so bash has read the entire script first
if [[ ! -t 0 ]]; then
    main "$@" < /dev/tty
else
    main "$@"
fi
