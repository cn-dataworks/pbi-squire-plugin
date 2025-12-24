# Visual Templates

Visual templates are maintained in a **public repository** for community contributions.

## Template Repository

**GitHub:** https://github.com/cn-dataworks/pbir-visuals

```
pbir-visuals/
└── visual-templates/
    ├── card-single-measure.json
    ├── line-chart-category-y.json
    ├── bar-chart-with-series.json
    └── ... (17+ templates)
```

## Using Templates

The skill automatically fetches templates from the public repository:

```
# Fetch latest templates
WebFetch: https://raw.githubusercontent.com/cn-dataworks/pbir-visuals/main/visual-templates/[template].json
```

## Contributing Templates

Anyone can contribute new templates:

1. **Fork** the [pbir-visuals](https://github.com/cn-dataworks/pbir-visuals) repository
2. **Add** your template to `visual-templates/`
3. **Submit** a Pull Request

See [CONTRIBUTING.md](https://github.com/cn-dataworks/pbir-visuals/blob/main/CONTRIBUTING.md) for guidelines.

## Harvesting Templates

Use `/harvest-templates` to extract templates from your reports:

```
/harvest-templates     → Extract to local staging
/review-templates      → Compare with public library
/promote-templates     → Create PR to public repo
```

## Why Public?

- **Community contributions** - Anyone can add templates
- **Version control** - Track template changes over time
- **Discoverability** - Templates are searchable on GitHub
- **Independence** - Works without this private skill installed
