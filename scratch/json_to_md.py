import json

def generate_md():
    with open("scratch/openapi.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    out = []
    out.append("# 📖 Swagger API Reference (Detailed)\n")
    out.append("> **Otomatis Dihasilkan**: Dokumen ini ditarik langsung dari kerangka kerja `OpenAPI` FastAPI. Rujukan ini memuat struktur metode (*Methods*), format input (*Payloads*), dan penempatan parameter.\n")
    
    paths = data.get("paths", {})
    
    # Kelompokkan berdasarkan Tag (seperti di Swagger UI)
    tags_map = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            tags = details.get("tags", ["General"])
            tag = tags[0]
            if tag not in tags_map:
                tags_map[tag] = []
            tags_map[tag].append({
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "requestBody": details.get("requestBody", {}),
                "parameters": details.get("parameters", [])
            })
            
    for tag, endpoints in sorted(tags_map.items()):
        out.append(f"## 🏷️ Tag: {tag.title()}\n")
        for ep in endpoints:
            # Berikan gaya khusus untuk tipe HTTP
            method_color = "🟢" if ep['method'] == "GET" else "🔵" if ep['method'] == "POST" else "🟠" if ep['method'] == "PUT" else "🔴" if ep['method'] == "DELETE" else "⚪"
            out.append(f"### {method_color} `{ep['method']}` {ep['path']}")
            
            if ep['summary']:
                out.append(f"> **{ep['summary']}**\n")
            if ep['description']:
                out.append(f"{ep['description']}\n")
                
            # Render Parameters (Query/Path)
            if ep['parameters']:
                out.append("**📥 Parameters:**")
                out.append("| Nama Parameter | Lokasi (In) | Wajib? | Tipe Data |")
                out.append("|---|---|---|---|")
                for p in ep['parameters']:
                    p_name = p.get('name')
                    p_in = p.get('in')
                    p_req = "✅ Ya" if p.get('required') else "❌ Opsional"
                    p_type = p.get('schema', {}).get('type', 'string')
                    out.append(f"| `{p_name}` | `{p_in}` | {p_req} | `{p_type}` |")
                out.append("")
                
            # Render Request Body
            if ep['requestBody']:
                out.append("**📤 Request Body (Payload):**")
                content = ep['requestBody'].get('content', {})
                if 'application/json' in content:
                    ref = content['application/json'].get('schema', {}).get('$ref', '')
                    if ref:
                        model_name = ref.split("/")[-1]
                        out.append(f"- Membutuhkan `JSON` dengan struktur skema: **`{model_name}`**\n")
                    else:
                        out.append("- Membutuhkan struktur `JSON` mentah.\n")
                elif 'multipart/form-data' in content:
                    out.append("- 📁 Membutuhkan `Form-Data` (Biasanya untuk unggahan File/Gambar).\n")
                elif 'application/x-www-form-urlencoded' in content:
                    out.append("- 📝 Membutuhkan `Form-URLEncoded` (Standar OAuth2/Login).\n")
            out.append("---\n")
            
    with open("docs/backend/openapi-reference.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

generate_md()
print("Markdown Swagger API docs generated successfully.")
