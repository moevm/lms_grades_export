def generate_from_base_html(title, content):
    """Базовый HTML шаблон для всех страниц"""
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --light-bg: #ecf0f1;
            --dark-text: #2c3e50;
            --light-text: #7f8c8d;
            --border-color: #bdc3c7;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--dark-text);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid var(--secondary-color);
        }}
        
        .card h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--light-bg);
        }}
        
        .card h3 {{
            color: var(--secondary-color);
            margin: 20px 0 15px 0;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .info-item {{
            background: var(--light-bg);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid var(--secondary-color);
        }}
        
        .info-label {{
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 5px;
            display: block;
        }}
        
        .info-value {{
            color: var(--dark-text);
            font-size: 1.1em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background: var(--light-bg);
            transition: background 0.3s ease;
        }}
        
        .rating-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 2px;
        }}
        
        .rating-excellent {{
            background: var(--success-color);
            color: white;
        }}
        
        .rating-good {{
            background: #f39c12;
            color: white;
        }}
        
        .rating-normal {{
            background: var(--secondary-color);
            color: white;
        }}
        
        .rating-warning {{
            background: var(--warning-color);
            color: white;
        }}
        
        .rating-problem {{
            background: var(--accent-color);
            color: white;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 25px;
            background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
            color: white;
            text-decoration: none;
            border-radius: 25px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .btn-back {{
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: var(--light-bg);
            color: var(--light-text);
            margin-top: 30px;
        }}
        
        .last-update {{
            font-size: 0.9em;
            color: var(--light-text);
            text-align: right;
            margin-top: 20px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""
