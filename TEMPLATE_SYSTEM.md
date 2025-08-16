# Template Management System

The Cockpit Template Management System allows you to work with multiple configuration templates from different sources. This system has been designed to replace the previous single-template approach with a more flexible multi-template architecture.

## Features

### Multiple Template Sources

- **Git Repository**: Templates stored in Git repositories with automatic synchronization
- **File Upload**: Templates uploaded directly through the web interface
- **Web Editor**: Templates created and edited using the built-in web editor

### Template Management

- **Multiple Templates**: Support for unlimited number of templates
- **Categorization**: Organize templates by categories (Network, Security, etc.)
- **Version History**: Track changes to templates over time
- **Search & Filter**: Find templates by name, category, description, or content

### Template Types

- **Jinja2**: Advanced templating with variables and logic
- **Plain Text**: Simple text-based templates
- **YAML**: YAML-formatted templates
- **JSON**: JSON-formatted templates

## Architecture

### Backend Components

#### Template Manager (`template_manager.py`)

- Handles template storage, retrieval, and management
- SQLite database for template metadata
- File system storage for template content
- Version control and history tracking

#### Template Router (`routers/templates.py`)

- REST API endpoints for template operations
- CRUD operations (Create, Read, Update, Delete)
- Import/export functionality
- Template rendering with variables

#### Template Models (`models/templates.py`)

- Pydantic models for request/response validation
- Type definitions for template sources and types
- Data validation and serialization

### Frontend Components

#### Template Settings Page (`production/settings-templates.html`)

- Tabbed interface for template management
- Template list with search and filtering
- Template creation form with source-specific options
- Bulk import functionality

### Database Schema

#### Templates Table

```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('git', 'file', 'webeditor')),
    template_type TEXT NOT NULL DEFAULT 'jinja2',
    category TEXT,
    description TEXT,

    -- Git-specific fields
    git_repo_url TEXT,
    git_branch TEXT DEFAULT 'main',
    git_username TEXT,
    git_token TEXT,
    git_path TEXT,
    git_verify_ssl BOOLEAN DEFAULT 1,

    -- File/WebEditor fields
    content TEXT,
    filename TEXT,
    content_hash TEXT,

    -- Metadata
    variables TEXT DEFAULT '{}',
    tags TEXT DEFAULT '[]',

    -- Status
    is_active BOOLEAN DEFAULT 1,
    last_sync TIMESTAMP,
    sync_status TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Template Versions Table

```sql
CREATE TABLE template_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    change_notes TEXT,
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE
)
```

## API Endpoints

### Template Management

- `GET /api/templates` - List all templates
- `POST /api/templates` - Create new template
- `GET /api/templates/{id}` - Get specific template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `GET /api/templates/name/{name}` - Get template by name

### Template Content

- `GET /api/templates/{id}/content` - Get template content
- `POST /api/templates/{id}/render` - Render template with variables
- `GET /api/templates/{id}/versions` - Get template version history

### Template Operations

- `POST /api/templates/upload` - Upload template file
- `POST /api/templates/sync` - Sync Git templates
- `POST /api/templates/import` - Bulk import templates
- `POST /api/templates/git/test` - Test Git connection

### Categories and Search

- `GET /api/templates/categories` - Get all categories
- `GET /api/templates?search=query` - Search templates

## Usage Examples

### Creating a Git Template

```json
POST /api/templates
{
    "name": "cisco-ios-base",
    "source": "git",
    "template_type": "jinja2",
    "category": "Network",
    "description": "Base Cisco IOS configuration",
    "git_repo_url": "https://github.com/user/templates.git",
    "git_branch": "main",
    "git_path": "cisco/ios-base.j2",
    "git_username": "username",
    "git_token": "token"
}
```

### Creating a Web Editor Template

```json
POST /api/templates
{
    "name": "switch-config",
    "source": "webeditor",
    "template_type": "jinja2",
    "category": "Network",
    "description": "Switch configuration template",
    "content": "hostname {{ hostname }}\n!\ninterface {{ interface }}\n description {{ description }}"
}
```

### Rendering a Template

```json
POST /api/templates/1/render
{
    "template_id": 1,
    "variables": {
        "hostname": "sw01",
        "interface": "GigabitEthernet0/1",
        "description": "Uplink to core"
    }
}
```

## File Structure

```
backend/
├── template_manager.py          # Template management core
├── models/templates.py          # Template data models
├── routers/templates.py         # Template API endpoints
└── main.py                      # FastAPI app with template router

production/
├── settings-templates.html      # Template management interface
└── settings-templates-old.html  # Backup of old interface

data/
├── templates/                   # Template file storage
└── settings/
    └── cockpit_templates.db     # Template metadata database
```

## Migration from Old System

The old single-template system has been replaced with this multi-template system. The old template settings page has been backed up to `settings-templates-old.html` and replaced with the new interface.

### Legacy API Support

- Old template settings endpoints (`/api/settings/templates`) now return redirect messages
- Existing configurations are not automatically migrated
- Users need to recreate templates using the new interface

## Development Notes

### Adding New Template Sources

1. Add source type to `TemplateSource` enum in `models/templates.py`
2. Update template creation logic in `template_manager.py`
3. Add UI support in the frontend template form
4. Update validation and testing

### Extending Template Types

1. Add type to `TemplateType` enum in `models/templates.py`
2. Update template rendering logic if needed
3. Add UI support for the new type
4. Update validation and file handling

### Future Enhancements

- [ ] Jinja2 template rendering with proper error handling
- [ ] Git repository synchronization automation
- [ ] Template validation and linting
- [ ] Template sharing between instances
- [ ] Advanced variable management
- [ ] Template inheritance and composition
- [ ] Backup and restore functionality
- [ ] Audit logging for template changes
