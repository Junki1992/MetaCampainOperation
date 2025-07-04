// メインJavaScriptファイル

// ページ読み込み完了時の処理
$(document).ready(function() {
    // アラートの自動非表示
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // テーブルのソート機能（簡易版）
    $('.table th').click(function() {
        const table = $(this).closest('table');
        const tbody = table.find('tbody');
        const rows = tbody.find('tr').toArray();
        const columnIndex = $(this).index();
        
        rows.sort(function(a, b) {
            const aText = $(a).find('td').eq(columnIndex).text().trim();
            const bText = $(b).find('td').eq(columnIndex).text().trim();
            return aText.localeCompare(bText, 'ja');
        });
        
        tbody.empty().append(rows);
    });
    
    // ツールチップの初期化
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // ポップオーバーの初期化
    $('[data-bs-toggle="popover"]').popover();
});

// ユーティリティ関数
const CampaignManager = {
    // キャンペーンの停止・起動切り替え
    toggleCampaign: function(campaignId, action) {
        const actionText = action === 'start' ? '開始' : '停止';
        
        if (!confirm(`キャンペーンを${actionText}しますか？`)) {
            return;
        }
        
        $.ajax({
            url: '/campaigns/ajax/toggle/',
            method: 'POST',
            data: JSON.stringify({
                campaign_id: campaignId,
                action: action
            }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    this.showAlert('success', response.message);
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    this.showAlert('danger', response.message);
                }
            }.bind(this),
            error: function() {
                this.showAlert('danger', '操作に失敗しました。');
            }.bind(this)
        });
    },
    
    // キャンペーン同期
    syncCampaigns: function(accountId) {
        if (!confirm('キャンペーンを同期しますか？')) {
            return;
        }
        
        $.ajax({
            url: '/campaigns/ajax/sync/',
            method: 'POST',
            data: JSON.stringify({
                account_id: accountId
            }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    this.showAlert('success', response.message);
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    this.showAlert('danger', response.message);
                }
            }.bind(this),
            error: function() {
                this.showAlert('danger', '同期に失敗しました。');
            }.bind(this)
        });
    },
    
    // アラート表示
    showAlert: function(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('.container').first().prepend(alertHtml);
    },
    
    // CSRFトークン取得
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    
    // 数値のフォーマット
    formatNumber: function(num) {
        return new Intl.NumberFormat('ja-JP').format(num);
    },
    
    // 通貨のフォーマット
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('ja-JP', {
            style: 'currency',
            currency: 'JPY'
        }).format(amount);
    },
    
    // パーセンテージのフォーマット
    formatPercentage: function(value) {
        return (value * 100).toFixed(2) + '%';
    }
};

// グローバル関数として公開
window.CampaignManager = CampaignManager; 