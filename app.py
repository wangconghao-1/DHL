<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DHL Knowledge Base System</title>
    <style>
        /* basic */
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }
        .navbar { background: #d40511; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .logout-btn { background: #ffcc00; color: #d40511; text-decoration: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        .container { max-width: 1000px; margin: 25px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        
        /* submit */
        .form-section { background: #fff9f9; padding: 20px; border-left: 5px solid #d40511; margin-bottom: 30px; }
        .dhl-red { color: #d40511; margin-top: 0; }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        .submit-btn { background: #d40511; color: white; border: none; padding: 12px 25px; font-weight: bold; cursor: pointer; border-radius: 4px; transition: 0.3s; }
        .submit-btn:hover { background: #b0040e; }

        /* list */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8f8f8; font-weight: bold; }
        .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; background: #fff3cd; color: #856404; font-weight: bold; }
        .btn-view { background: #007bff; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; }

        /* model */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); }
        .modal-content { background: white; margin: 8% auto; padding: 30px; width: 70%; max-height: 80vh; overflow-y: auto; border-radius: 8px; position: relative; }
        .close-btn { position: absolute; right: 20px; top: 15px; font-size: 28px; cursor: pointer; color: #999; }
        .detail-label { font-weight: bold; color: #d40511; display: block; margin: 15px 0 5px 0; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .detail-text { white-space: pre-wrap; background: #fdfdfd; padding: 15px; border: 1px inset #eee; display: block; font-size: 14px; line-height: 1.6; }
    </style>
</head>
<body>

    <div class="navbar">
        <div style="font-size: 22px; font-weight: bold; letter-spacing: 1px;">DHL KB PORTAL</div>
        <a href="/logout" class="logout-btn">LOGOUT</a>
    </div>

    <div class="container">
        <div class="form-section">
            <h3 class="dhl-red">Create New SOP Draft</h3>
            <input type="text" id="title" placeholder="Enter SOP Title (e.g. Onboarding Process)">
            <textarea id="content" rows="4" placeholder="Paste raw content or messy notes here..."></textarea>
            <button class="submit-btn" onclick="submitSOP()">SUBMIT TO DATABASE</button>
        </div>

        <h3 class="dhl-red">Knowledge Articles List</h3>
        <input type="text" id="search" placeholder="Quick search by title..." onkeyup="filterTable()">
        
        <table id="sopTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>

    <div id="detailModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 class="dhl-red">Article Detailed View</h2>
            <div>
                <span class="detail-label">Title:</span>
                <div id="detailTitleText" style="font-size: 18px; font-weight: bold;"></div>
                
                <span class="detail-label">Status:</span>
                <span id="detailStatus" class="status-badge"></span>

                <span class="detail-label">Content:</span>
                <div id="detailContentText" class="detail-text"></div>
            </div>
            <div style="margin-top: 20px; text-align: right;">
                <button onclick="closeModal()" style="padding: 10px 25px; cursor:pointer; background:#666; color:white; border:none; border-radius:4px;">Close</button>
            </div>
        </div>
    </div>

    <script>
        let allArticles = [];

        // 初始化加载
        async function fetchArticles() {
            try {
                const response = await fetch('/api/articles');
                allArticles = await response.json();
                renderTable(allArticles);
            } catch (err) { console.error("Load failed:", err); }
        }

        // --- Submit 功能实现 ---
        async function submitSOP() {
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;

            if(!title || !content) {
                alert("Please complete both Title and Content fields.");
                return;
            }

            const response = await fetch('/api/articles', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title, content })
            });

            if(response.ok) {
                document.getElementById('title').value = '';
                document.getElementById('content').value = '';
                fetchArticles(); // 成功后刷新列表
            }
        }

        function renderTable(articles) {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = articles.map(a => `
                <tr>
                    <td>${a.id}</td>
                    <td>${a.title}</td>
                    <td><span class="status-badge">${a.status}</span></td>
                    <td>
                        <button class="btn-view" onclick="showDetail(${a.id})">View Details</button>
                    </td>
                </tr>
            `).join('');
        }

        function showDetail(id) {
            const article = allArticles.find(a => a.id === id);
            if (article) {
                document.getElementById('detailTitleText').innerText = article.title;
                document.getElementById('detailContentText').innerText = article.content;
                document.getElementById('detailStatus').innerText = article.status;
                document.getElementById('detailModal').style.display = 'block';
            }
        }

        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }

        function filterTable() {
            const query = document.getElementById('search').value.toLowerCase();
            const filtered = allArticles.filter(a => a.title.toLowerCase().includes(query));
            renderTable(filtered);
        }

        window.onclick = (e) => { if (e.target == document.getElementById('detailModal')) closeModal(); }
        window.onload = fetchArticles;
    </script>
</body>
</html>

