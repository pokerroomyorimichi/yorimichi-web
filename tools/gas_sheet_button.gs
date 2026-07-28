/**
 * YORIMICHI 公式HP 社員更新システム — Googleシート用 Apps Script
 * 機能:
 *   ① 今すぐ反映  : GitHub Actions を即時起動（5分待たず公開）
 *   ② 場所リスト更新: 公開CSV(slots.csv)を取得して「_一覧」を最新化（新記事の箇所もプルダウンに追加）
 *
 * 【設置手順】
 *   1) シートで 拡張機能 → Apps Script を開き、このコードを貼り付けて保存
 *   2) プロジェクトの設定 → スクリプト プロパティ に GITHUB_TOKEN を登録
 *      （GitHubの Fine-grained PAT。対象リポジトリ=pokerroomyorimichi/yorimichi-web、
 *        権限: Contents = Read and write。※「今すぐ反映」だけに必要。②は不要）
 *   3) シートを再読み込みするとメニュー「YORIMICHI HP更新」が出る
 *   4) 任意: setupTrigger() を1回実行すると、1時間ごとに②を自動実行（新記事を自動でプルダウンへ）
 */

var REPO = 'pokerroomyorimichi/yorimichi-web';
var SLOTS_CSV = 'https://pokerroomyorimichi.github.io/yorimichi-web/data/slots.csv';
var LIST_SHEET = '_一覧';

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('YORIMICHI HP更新')
    .addItem('① 今すぐ反映（すぐ公開）', 'publishNow')
    .addItem('② 場所リストを更新（新記事を反映）', 'refreshSlots')
    .addSeparator()
    .addItem('自動更新をON（1時間ごと）', 'setupTrigger')
    .addToUi();
}

/** ① GitHub Actions を即時起動 */
function publishNow() {
  var ui = SpreadsheetApp.getUi();
  var token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) {
    ui.alert('GITHUB_TOKEN が未設定です。スクリプト プロパティに登録してください。');
    return;
  }
  var res = UrlFetchApp.fetch('https://api.github.com/repos/' + REPO + '/dispatches', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' },
    payload: JSON.stringify({ event_type: 'hp-update' }),
    muteHttpExceptions: true
  });
  var code = res.getResponseCode();
  if (code === 204) {
    SpreadsheetApp.getActiveSpreadsheet().toast('反映を開始しました。約1分で公開されます。', 'YORIMICHI HP更新', 5);
  } else {
    ui.alert('起動に失敗しました (HTTP ' + code + ')\n' + res.getContentText());
  }
}

/** ② 公開CSVから「_一覧」を最新化（新記事の箇所も追加） */
function refreshSlots() {
  var res = UrlFetchApp.fetch(SLOTS_CSV + '?t=' + Date.now(), { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) {
    SpreadsheetApp.getUi().alert('CSV取得に失敗 (HTTP ' + res.getResponseCode() + ')');
    return;
  }
  var rows = Utilities.parseCsv(res.getContentText());   // [[label,slotId,種別,ページ], ...]
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(LIST_SHEET);
  if (!sh) { sh = ss.insertSheet(LIST_SHEET); }
  sh.clearContents();
  var out = [['場所ラベル', 'slotId', '種別', 'ページ']].concat(rows);
  sh.getRange(1, 1, out.length, 4).setValues(out);
  ss.toast('場所リストを更新しました（' + rows.length + '件）', 'YORIMICHI HP更新', 5);
}

/** 1時間ごとに②を自動実行するトリガーを設定 */
function setupTrigger() {
  var have = ScriptApp.getProjectTriggers().some(function (t) {
    return t.getHandlerFunction() === 'refreshSlots';
  });
  if (!have) {
    ScriptApp.newTrigger('refreshSlots').timeBased().everyHours(1).create();
  }
  SpreadsheetApp.getUi().alert('自動更新をONにしました（1時間ごとに場所リストを更新します）。');
}
