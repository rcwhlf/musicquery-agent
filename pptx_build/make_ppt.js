// MusicQuery Agent 答辩 PPT 生成脚本（pptxgenjs）
// 视觉主题：黑胶唱片 —— 深墨紫底 + 紫罗兰主色 + 琥珀点缀；同心圆为贯穿元素
const pptxgen = require("pptxgenjs");

const p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.33 × 7.5
p.author = "MusicQuery Agent";
p.title = "MusicQuery Agent 答辩";

// ---------- 调色板 ----------
const BG = "FFFFFF", BG_DARK = "171226";
const PRIMARY = "5B4AA8", PRIMARY_DK = "3E3080";
const TINT = "F1EEFA", TINT2 = "E9E4F7";
const ACCENT = "E8A33D";
const TEXT = "241F35", MUTED = "6F6A80", LINE = "E4E1EE";
const D_MUTED = "B9B3CC"; // 深色页上的次要文字
const F = "Microsoft YaHei";
const W = 13.33, H = 7.5, M = 0.6, CW = W - 2 * M;

// ---------- 公共元素 ----------
function kicker(s, txt) {
  s.addText(txt, { x: M, y: 0.38, w: 8, h: 0.32, fontSize: 12.5, bold: true, color: ACCENT, fontFace: F, charSpacing: 2, margin: 0 });
}
function title(s, txt) {
  s.addText(txt, { x: M, y: 0.68, w: CW, h: 0.62, fontSize: 27, bold: true, color: TEXT, fontFace: F, margin: 0 });
}
function badge(s, n) { // 黑胶页码徽标
  s.addShape(p.shapes.OVAL, { x: 12.42, y: 6.92, w: 0.36, h: 0.36, line: { color: LINE, width: 1.25 } });
  s.addText(String(n).padStart(2, "0"), { x: 12.42, y: 6.92, w: 0.36, h: 0.36, fontSize: 12, color: MUTED, fontFace: F, align: "center", valign: "middle", margin: 0 });
}
function arrow(s, x1, y1, x2, y2, color) {
  s.addShape(p.shapes.LINE, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: color || MUTED, width: 1.5, endArrowType: "triangle" } });
}
const bu = () => ({ code: "2013", indent: 10 });

// ================= S1 封面 =================
let s = p.addSlide();
s.background = { color: BG_DARK };
[[7.8, 1.15, 5.2, "2E2650", 1.5], [8.35, 1.7, 4.1, "38305C", 1.25], [8.9, 2.25, 3.0, "453A70", 1.25], [9.45, 2.8, 1.9, "534686", 1.25]].forEach(([x, y, d, c, wd]) => {
  s.addShape(p.shapes.OVAL, { x, y, w: d, h: d, line: { color: c, width: wd } });
});
s.addShape(p.shapes.OVAL, { x: 10.19, y: 3.54, w: 0.42, h: 0.42, fill: { color: ACCENT } });
s.addText("数据库系统课程 · 项目答辩", { x: 0.7, y: 1.85, w: 6.6, h: 0.4, fontSize: 14, bold: true, color: ACCENT, fontFace: F, charSpacing: 2, margin: 0 });
s.addText("MusicQuery Agent", { x: 0.7, y: 2.3, w: 7.0, h: 1.05, fontSize: 52, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
s.addText("基于自然语言交互的音乐作品库\n智能查询系统", { x: 0.7, y: 3.6, w: 6.6, h: 1.15, fontSize: 21, color: D_MUTED, fontFace: F, lineSpacingMultiple: 1.25, margin: 0 });
s.addText([
  { text: "核心思路：", options: { bold: true, color: ACCENT } },
  { text: "数据库设计是核心，Agent 是交互层", options: { color: D_MUTED } },
], { x: 0.7, y: 5.0, w: 6.6, h: 0.45, fontSize: 15, fontFace: F, margin: 0 });
s.addText("汇报人：________　　　指导教师：________", { x: 0.7, y: 6.3, w: 7.0, h: 0.4, fontSize: 13, color: D_MUTED, fontFace: F, margin: 0 });
s.addNotes("各位老师好。我答辩的项目是 MusicQuery Agent——基于自然语言交互的音乐作品库智能查询系统。一句话定位：用户用中文提问，系统自动把问题转成 SQL、查询 MySQL 数据库，再用不超过 50 字的自然语言回答。整个项目里，数据库设计是核心，Agent 只是交互层。");

// ================= S2 系统定位 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "01 · 系统定位"); title(s, "用中文提问，返回自然语言答案");
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 3.1, w: 1.5, h: 1.2, rectRadius: 0.08, fill: { color: TINT }, line: { color: PRIMARY, width: 1 } });
s.addText("用户提问\n（中文）", { x: M, y: 3.1, w: 1.5, h: 1.2, fontSize: 14, bold: true, color: PRIMARY_DK, fontFace: F, align: "center", valign: "middle", margin: 0 });
const steps2 = [
  ["01", "意图判断", "LLM 守门员判定相关性"],
  ["02", "SQL 生成", "DDL 写入 Prompt，仅允许 SELECT"],
  ["03", "执行校验", "三道防线 + 失败自动重试"],
  ["04", "结果解释", "生成 50 字以内中文结论"],
];
steps2.forEach(([n, t, d], i) => {
  const x = 2.55 + i * 2.1;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.85, w: 1.98, h: 1.7, rectRadius: 0.08, fill: { color: BG }, line: { color: LINE, width: 1 }, shadow: { type: "outer", color: "241F35", blur: 7, offset: 2, angle: 90, opacity: 0.12 } });
  s.addText(n, { x: x + 0.18, y: 3.0, w: 1.6, h: 0.5, fontSize: 25, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
  s.addText(t, { x: x + 0.18, y: 3.52, w: 1.65, h: 0.36, fontSize: 16.5, bold: true, color: TEXT, fontFace: F, margin: 0 });
  s.addText(d, { x: x + 0.18, y: 3.9, w: 1.66, h: 0.6, fontSize: 11.5, color: MUTED, fontFace: F, lineSpacingMultiple: 1.12, margin: 0 });
  if (i < 3) arrow(s, x + 1.98, 3.7, x + 2.1, 3.7);
});
arrow(s, M + 1.5, 3.7, 2.53, 3.7);
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 11.22, y: 3.1, w: 1.51, h: 1.2, rectRadius: 0.08, fill: { color: PRIMARY }, line: { color: PRIMARY, width: 1 } });
s.addText("自然语言\n回答", { x: 11.22, y: 3.1, w: 1.51, h: 1.2, fontSize: 14, bold: true, color: "FFFFFF", fontFace: F, align: "center", valign: "middle", margin: 0 });
arrow(s, 11.01, 3.7, 11.2, 3.7);
s.addShape(p.shapes.RECTANGLE, { x: 0, y: 5.35, w: W, h: 1.15, fill: { color: TINT } });
s.addText([
  { text: "技术栈　", options: { bold: true, color: PRIMARY_DK } },
  { text: "Python 3.10+ · MySQL 8.4 · PyMySQL · Streamlit · 智谱 GLM-5.3-Flash", options: { color: TEXT } },
], { x: 0.75, y: 5.35, w: 11.9, h: 1.15, fontSize: 14.5, fontFace: F, valign: "middle", margin: 0 });
badge(s, 2);
s.addNotes("系统是一条完整闭环：中文提问先经过意图判断这道守门员，无关问题直接礼貌拒绝；相关问题由大模型依据真实表结构生成 SQL，经三道安全防线校验后执行，执行失败还能把报错回传给大模型自动修正；最后把查询结果翻译成 50 字以内的自然语言回答。技术栈全部是课程内学过的 MySQL，加上 Python 生态的 Streamlit 网页界面。");

// ================= S3 ER 关系图 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "02 · 数据库设计"); title(s, "5 张业务表 + 1 张日志表");
function entity(x, y, name, fields, hot, dash) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.1, h: 1.66, rectRadius: 0.06, fill: { color: hot ? "FDF3E1" : BG }, line: { color: hot ? ACCENT : PRIMARY, width: hot ? 1.5 : 1.25, dashType: dash ? "dash" : "solid" } });
  s.addText(name, { x: x + 0.14, y: y + 0.08, w: 1.85, h: 0.32, fontSize: 14.5, bold: true, color: hot ? "9A6A12" : PRIMARY_DK, fontFace: F, margin: 0 });
  s.addText(fields, { x: x + 0.14, y: y + 0.44, w: 1.86, h: 1.15, fontSize: 12, color: MUTED, fontFace: F, lineSpacingMultiple: 1.08, margin: 0 });
}
entity(0.7, 1.55, "artists 歌手", "artist_id (PK)\nname · country\ndebut_year");
entity(3.5, 1.55, "albums 专辑", "album_id (PK)\ntitle · artist_id (FK)\nrelease_date · album_type", false);
entity(6.3, 1.55, "songs 歌曲", "song_id (PK)\nalbum_id FK · artist_id FK\nduration_sec · genre\nrelease_year");
entity(0.7, 4.85, "users 用户", "user_id (PK)\nnickname · city\nregister_date");
entity(3.5, 4.85, "play_records 播放记录", "record_id (PK)\nsong_id FK · user_id FK\nplay_time · device", true);
entity(6.3, 4.85, "query_logs 查询日志", "user_question · sql\nis_success · 耗时\nAgent 每次查询写入", false, true);
const seg = (x, y, w, h) => s.addShape(p.shapes.LINE, { x, y, w, h, line: { color: MUTED, width: 1.5 } });
seg(2.8, 2.38, 0.7, 0); s.addText("1 : N", { x: 2.78, y: 2.0, w: 0.75, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
seg(5.6, 2.38, 0.7, 0); s.addText("1 : N", { x: 5.58, y: 2.0, w: 0.75, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
seg(1.75, 3.21, 0, 0.89); seg(1.75, 4.1, 5.6, 0); seg(7.35, 3.21, 0, 0.89);
s.addText("artist_id 直连（1 : N）", { x: 3.15, y: 4.16, w: 2.2, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
s.addShape(p.shapes.LINE, { x: 5.65, y: 3.21, w: 0.9, h: 1.64, flipH: true, line: { color: MUTED, width: 1.5 } });
s.addText("song_id", { x: 6.7, y: 4.25, w: 1.0, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
seg(2.8, 5.68, 0.7, 0); s.addText("1 : N", { x: 2.78, y: 5.32, w: 0.75, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
s.addText("琥珀色 = 事实表 play_records：一条记录代表一次播放，与维度表构成星型访问结构", { x: 0.7, y: 6.72, w: 7.8, h: 0.35, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
const pts3 = [
  ["职责单一", "5 张业务表各司其职，query_logs 独立记录 Agent 行为"],
  ["引用完整", "全部 InnoDB 引擎 + 外键约束，非法数据写不进来"],
  ["星型访问", "事实表居中，按歌曲、用户、时间多路径统计都清晰"],
];
pts3.forEach(([t, d], i) => {
  s.addText([
    { text: t, options: { bold: true, fontSize: 15.5, color: PRIMARY_DK, breakLine: true } },
    { text: d, options: { fontSize: 12.5, color: MUTED } },
  ], { x: 8.85, y: 1.7 + i * 1.62, w: 3.85, h: 1.4, fontFace: F, lineSpacingMultiple: 1.15, margin: 0 });
});
badge(s, 3);
s.addNotes("数据库一共 6 张表：歌手、专辑、歌曲、用户四张维度表，加一张事实表 play_records——一条记录代表一次播放，查询路径像星星一样从事实表向四周发散，按歌曲、按用户、按时间统计都很自然。第六张 query_logs 是 Agent 自己的查询日志表，记录每次的问题、生成的 SQL、是否成功和耗时。全部表使用 InnoDB 并建了外键约束，引用完整性由数据库本身保证，而不是靠应用程序自觉。");

// ================= S4 设计决策 + 数据规模 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "03 · 表结构设计"); title(s, "四个关键设计决策");
const rows4 = [
  ["受控冗余", "songs 同时持有 album_id 与 artist_id：按歌手查歌免二次 JOIN，一致性由导入层保证"],
  ["满足三范式", "各表非主属性完全、直接依赖于主键；专辑与歌曲中的歌手信息只存 ID 不存名字"],
  ["ENUM 约束", "album_type 取值限定 studio / live / compilation，在数据库层挡住脏数据"],
  ["事实表用 BIGINT", "play_records 增长最快，BIGINT 主键为规模化预留空间（INT 上限约 21 亿）"],
];
rows4.forEach(([t, d], i) => {
  s.addText([
    { text: t, options: { bold: true, fontSize: 16.5, color: TEXT, breakLine: true } },
    { text: d, options: { fontSize: 13, color: MUTED } },
  ], { x: 0.7, y: 1.62 + i * 1.28, w: 7.0, h: 1.1, fontFace: F, lineSpacingMultiple: 1.18, margin: 0 });
  if (i) s.addShape(p.shapes.LINE, { x: 0.7, y: 1.5 + i * 1.28, w: 7.0, h: 0, line: { color: LINE, width: 1 } });
});
s.addText("测试数据规模", { x: 8.35, y: 1.55, w: 4.3, h: 0.35, fontSize: 14, bold: true, color: MUTED, fontFace: F, margin: 0 });
const stats4 = [["50", "歌手", 24], ["100", "专辑", 24], ["500", "歌曲", 24], ["200", "用户", 24], ["5000", "播放记录", 40]];
stats4.forEach(([n, l, fs], i) => {
  const y = 2.0 + i * 0.98;
  s.addText(n, { x: 8.35, y, w: 1.85, h: 0.85, fontSize: fs, bold: true, color: ACCENT, fontFace: F, align: "right", valign: "middle", margin: 0 });
  s.addText(l, { x: 10.35, y: y + (fs > 30 ? 0.18 : 0.14), w: 2.3, h: 0.5, fontSize: 14, color: TEXT, fontFace: F, valign: "middle", margin: 0 });
  if (i < 4) s.addShape(p.shapes.LINE, { x: 8.35, y: y + 0.92, w: 4.2, h: 0, line: { color: LINE, width: 1 } });
});
badge(s, 4);
s.addNotes("讲四个决策。第一，受控冗余：songs 表同时存了专辑 ID 和歌手 ID，按歌手查歌不需要绕道专辑表做二次 JOIN，代价是一致性要靠导入层保证，这是有意识的取舍。第二，整体满足三范式，名字类的冗余信息都不存。第三，专辑类型用 ENUM 枚举，在数据库层就挡住脏数据。第四，事实表主键用 BIGINT，因为它增长最快。右侧是测试数据规模：50 歌手、100 专辑、500 歌曲、200 用户、5000 条播放记录，与任务书要求完全一致。");

// ================= S5 索引设计 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "04 · 索引设计"); title(s, "为高频查询建索引，并用 EXPLAIN 验证");
const idx5 = [
  ["idx_songs_artist", "songs(artist_id)", "按歌手查歌曲、按歌手统计播放"],
  ["idx_songs_genre_year", "songs(genre, release_year) 复合", "流派 + 年份组合筛选，最左前缀原则"],
  ["idx_play_time", "play_records(play_time)", "按时间范围过滤播放记录"],
  ["idx_play_song_time", "play_records(song_id, play_time) 复合", "单曲播放量统计：先等值再范围"],
];
idx5.forEach(([n, c, u], i) => {
  const y = 1.52 + i * 0.78;
  s.addText(n, { x: 0.7, y, w: 3.25, h: 0.62, fontSize: 13.5, bold: true, color: PRIMARY_DK, fontFace: "Consolas", valign: "middle", margin: 0 });
  s.addText(c, { x: 4.05, y, w: 3.7, h: 0.62, fontSize: 12.5, color: TEXT, fontFace: F, valign: "middle", margin: 0 });
  s.addText(u, { x: 7.85, y, w: 4.85, h: 0.62, fontSize: 12.5, color: MUTED, fontFace: F, valign: "middle", margin: 0 });
  if (i < 3) s.addShape(p.shapes.LINE, { x: 0.7, y: y + 0.7, w: 11.95, h: 0, line: { color: LINE, width: 1 } });
});
s.addShape(p.shapes.RECTANGLE, { x: 0, y: 4.85, w: W, h: 2.05, fill: { color: TINT } });
s.addText("EXPLAIN 实证（本机 MySQL 8.4.9）", { x: 0.75, y: 5.0, w: 8, h: 0.35, fontSize: 14, bold: true, color: PRIMARY_DK, fontFace: F, margin: 0 });
s.addText([
  { text: "genre + 年份　→ type=range，命中 ", options: { color: TEXT } },
  { text: "idx_songs_genre_year", options: { bold: true, color: PRIMARY_DK } },
  { text: "，Using index condition", options: { color: TEXT, breakLine: true } },
  { text: "song_id + 时间 → 优化器选中复合索引 ", options: { color: TEXT } },
  { text: "idx_play_song_time", options: { bold: true, color: PRIMARY_DK } },
  { text: "，Using index（覆盖索引，免回表）", options: { color: TEXT, breakLine: true } },
  { text: "play_time　　→ type=range，命中 ", options: { color: TEXT } },
  { text: "idx_play_time", options: { bold: true, color: PRIMARY_DK } },
  { text: "，扫描行数 240", options: { color: TEXT } },
], { x: 0.75, y: 5.42, w: 11.9, h: 1.4, fontSize: 13.5, fontFace: F, lineSpacingMultiple: 1.4, margin: 0 });
s.addText("数据来源：music_query 库 EXPLAIN 实测", { x: 0.75, y: 6.55, w: 7.0, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
badge(s, 5);
s.addNotes("四个索引全部对应真实的高频查询：两个单列索引解决按歌手查、按时间查；两个复合索引里，genre 和年份的顺序遵循最左前缀原则——等值高选择性的 genre 放左边。右下角是重点：我在这台机器的 MySQL 8.4 上跑过 EXPLAIN，三个代表性查询分别命中了设计的索引；最漂亮的是 song_id 加时间的查询，优化器在两个候选索引里自己选了复合索引，而且显示 Using index，说明是覆盖索引，连回表都省了。");

// ================= S6 Agent 四步流程 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "05 · Agent 流程"); title(s, "四步流水线：从问题到回答");
const cards6 = [
  ["01", "意图判断", ["LLM 只回答 YES / NO", "无关问题直接拦截", "提示“与音乐数据库无关”"]],
  ["02", "SQL 生成", ["建表 DDL 全文进 Prompt", "严格规则：仅允许 SELECT", "剥离代码块与多余解释"]],
  ["03", "执行校验", ["白名单 + 黑名单双校验", "报错回传 LLM 自动修正", "最多重试 2 次"]],
  ["04", "结果解释", ["结果转 JSON，截取前 15 条", "生成 ≤50 字中文结论", "解释失败不影响查询本身"]],
];
cards6.forEach(([n, t, items], i) => {
  const x = 0.6 + i * 3.08;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.86, h: 3.95, rectRadius: 0.09, fill: { color: i === 2 ? TINT : BG }, line: { color: i === 2 ? PRIMARY : LINE, width: i === 2 ? 1.5 : 1 }, shadow: { type: "outer", color: "241F35", blur: 7, offset: 2, angle: 90, opacity: 0.1 } });
  s.addText(n, { x: x + 0.22, y: 1.72, w: 1.5, h: 0.62, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
  s.addText(t, { x: x + 0.22, y: 2.38, w: 2.4, h: 0.42, fontSize: 17.5, bold: true, color: TEXT, fontFace: F, margin: 0 });
  s.addText(items.map((tx, j) => ({ text: tx, options: { bullet: bu(), breakLine: j < items.length - 1 } })), { x: x + 0.22, y: 2.95, w: 2.45, h: 2.3, fontSize: 12.5, color: MUTED, fontFace: F, paraSpaceAfter: 10, margin: 0 });
});
s.addShape(p.shapes.RECTANGLE, { x: 0, y: 5.85, w: W, h: 0.95, fill: { color: TINT2 } });
s.addText([
  { text: "单一数据源　", options: { bold: true, color: PRIMARY_DK } },
  { text: "Prompt 中的表结构运行时直接读取 db/schema.sql —— 修改表结构无需同步修改提示词", options: { color: TEXT } },
], { x: 0.75, y: 5.85, w: 11.9, h: 0.95, fontSize: 14, fontFace: F, valign: "middle", margin: 0 });
badge(s, 6);
s.addNotes("Agent 分四步。第一步意图判断，用一个小 Prompt 让模型只回答 YES 或 NO，无关问题一步拦截。第二步 SQL 生成，把建表语句全文和字段说明都写进提示词，并加了严格规则。第三步是核心，先做安全校验再执行，执行出错就把报错原文回传给大模型修正重试，最多两次，高亮卡片就是这一步。第四步把结果转成 JSON 传给模型，输出 50 字以内的中文结论。底部是个工程细节：提示词里的表结构是运行时直接读 schema.sql 的，改了表结构提示词自动跟着变，保证单一数据源。");

// ================= S7 安全设计 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "06 · 安全设计"); title(s, "三道防线，挡住 LLM 的“手滑”");
const rows7 = [
  ["01", "语句白名单", "只放行 SELECT / WITH 开头的查询，其余一律拒绝"],
  ["02", "关键词黑名单", "正则拦截 DROP、DELETE、UPDATE、INSERT、ALTER、TRUNCATE 等高危词"],
  ["03", "全程留痕", "query_logs 记录问题、SQL、是否成功、耗时——被拦截的请求同样可追溯"],
];
rows7.forEach(([n, t, d], i) => {
  s.addText(n, { x: 0.7, y: 1.72 + i * 1.55, w: 0.85, h: 0.6, fontSize: 26, bold: true, color: ACCENT, fontFace: F, margin: 0 });
  s.addText([
    { text: t, options: { bold: true, fontSize: 16.5, color: TEXT, breakLine: true } },
    { text: d, options: { fontSize: 12.5, color: MUTED } },
  ], { x: 1.65, y: 1.66 + i * 1.55, w: 5.0, h: 1.35, fontFace: F, lineSpacingMultiple: 1.18, margin: 0 });
});
const box7 = (x, y, t, fillC, txtC) => {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.15, h: 0.6, rectRadius: 0.07, fill: { color: fillC }, line: { color: PRIMARY, width: 1 } });
  s.addText(t, { x, y, w: 2.15, h: 0.6, fontSize: 13.5, bold: true, color: txtC, fontFace: F, align: "center", valign: "middle", margin: 0 });
};
box7(7.15, 1.6, "生成 SQL", BG, TEXT);
box7(7.15, 2.62, "安全校验", BG, TEXT);
box7(7.15, 3.64, "执行", BG, TEXT);
box7(7.15, 4.66, "写日志 · 返回结果", PRIMARY, "FFFFFF");
arrow(s, 8.22, 2.2, 8.22, 2.6); s.addText("通过", { x: 8.35, y: 2.24, w: 0.8, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
arrow(s, 8.22, 3.22, 8.22, 3.62); s.addText("通过", { x: 8.35, y: 3.26, w: 0.8, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
arrow(s, 8.22, 4.24, 8.22, 4.64); s.addText("成功", { x: 8.35, y: 4.28, w: 0.8, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
box7(10.15, 3.64, "报错回传 LLM 修正", "FDF3E1", "9A6A12");
arrow(s, 9.32, 3.94, 10.13, 3.94); s.addText("失败", { x: 9.42, y: 3.6, w: 0.7, h: 0.3, fontSize: 12, color: "9A6A12", fontFace: F, margin: 0 });
s.addShape(p.shapes.LINE, { x: 11.22, y: 2.92, w: 0, h: 0.7, line: { color: "9A6A12", width: 1.5 } });
s.addShape(p.shapes.LINE, { x: 9.32, y: 2.92, w: 1.9, h: 0, line: { color: "9A6A12", width: 1.5, beginArrowType: "triangle" } });
s.addText("修正后重新校验（≤ 2 次）", { x: 9.55, y: 2.56, w: 2.6, h: 0.3, fontSize: 12, color: "9A6A12", fontFace: F, margin: 0 });
s.addText("示例：要求“删除所有播放记录”时，DELETE 命中黑名单，请求被拒并写入日志", { x: 7.15, y: 5.55, w: 5.5, h: 0.75, fontSize: 12.5, color: MUTED, fontFace: F, lineSpacingMultiple: 1.2, margin: 0 });
badge(s, 7);
s.addNotes("安全是答辩老师最关心的问题，我们做了三道防线：第一，语句白名单，只放行 SELECT 开头的查询；第二，关键词黑名单，用正则拦住 DROP、DELETE、UPDATE 这些高危词；第三，全程留痕，query_logs 把每次请求连同是否被拦截都记下来，出了问题可以追溯。右边是失败自动修正的闭环：执行出错时把报错原文回传给大模型，修正后重新走一遍安全校验，最多两次。比如要求它删除所有播放记录，DELETE 一命中黑名单就直接被拒。");

// ================= S8 现场演示 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "07 · 现场演示"); title(s, "演示脚本：由浅入深 + 两个特殊场景");
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.5, w: 6.55, h: 5.15, rectRadius: 0.09, fill: { color: BG }, line: { color: LINE, width: 1.25 }, shadow: { type: "outer", color: "241F35", blur: 8, offset: 2, angle: 90, opacity: 0.12 } });
s.addText("MusicQuery Agent", { x: 0.9, y: 1.68, w: 3.5, h: 0.32, fontSize: 13, bold: true, color: PRIMARY_DK, fontFace: F, margin: 0 });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.9, y: 2.1, w: 4.25, h: 0.44, rectRadius: 0.07, line: { color: LINE, width: 1.25 } });
s.addText("请输入你的问题", { x: 1.05, y: 2.1, w: 3.5, h: 0.44, fontSize: 12, color: MUTED, fontFace: F, valign: "middle", margin: 0 });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 5.3, y: 2.1, w: 0.75, h: 0.44, rectRadius: 0.07, fill: { color: ACCENT } });
s.addText("查询", { x: 5.3, y: 2.1, w: 0.75, h: 0.44, fontSize: 12.5, bold: true, color: "FFFFFF", fontFace: F, align: "center", valign: "middle", margin: 0 });
const mock8 = [["生成的 SQL", "SELECT s.title, COUNT(*) … LIMIT 5"], ["查询结果（表格）", "共 5 条记录 · SQL 执行 12 ms"], ["自然语言回答", "《一个人的烟火》以 194 次播放居首……"]];
mock8.forEach(([t, d], i) => {
  const y = 2.78 + i * 1.02;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.9, y, w: 4.55, h: 0.85, rectRadius: 0.06, fill: { color: i === 2 ? TINT : BG }, line: { color: LINE, width: 1.25 } });
  s.addText([
    { text: t, options: { bold: true, fontSize: 12, color: PRIMARY_DK, breakLine: true } },
    { text: d, options: { fontSize: 12, color: MUTED } },
  ], { x: 1.08, y: y + 0.1, w: 4.2, h: 0.65, fontFace: F, lineSpacingMultiple: 1.12, margin: 0 });
});
s.addShape(p.shapes.LINE, { x: 6.15, y: 2.1, w: 0, h: 4.3, line: { color: LINE, width: 1 } });
s.addText("耗时\n状态\n历史\n记录", { x: 6.2, y: 2.6, w: 0.85, h: 3.4, fontSize: 12.5, color: MUTED, fontFace: F, align: "center", lineSpacingMultiple: 1.7, margin: 0 });
const demo8 = [
  ["“播放量最高的前 5 首歌？”", "三表 JOIN + ORDER BY + LIMIT"],
  ["“一共有多少首流行歌曲？”", "COUNT 聚合查询"],
  ["“今天天气怎么样？”", "意图守门员：与音乐数据库无关"],
  ["“删除所有播放记录”", "黑名单拦截，日志 is_success = 0"],
  ["侧边栏", "本次耗时、成功状态、历史可回溯"],
];
demo8.forEach(([q, r], i) => {
  s.addText([
    { text: q, options: { bold: true, fontSize: 14, color: TEXT, breakLine: true } },
    { text: "→ " + r, options: { fontSize: 12.5, color: MUTED } },
  ], { x: 7.55, y: 1.58 + i * 0.92, w: 5.15, h: 0.8, fontFace: F, lineSpacingMultiple: 1.15, margin: 0 });
});
s.addText("兜底预案：手机热点保障外网；另备一组成功运行截图", { x: 7.55, y: 6.25, w: 5.15, h: 0.35, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
badge(s, 8);
s.addNotes("演示按由浅入深来：先来一个多表 JOIN 的播放量排名，再来一个 COUNT 聚合；然后演示两个特殊场景——问天气，会被意图判断礼貌拒绝；要求删除播放记录，会被黑名单拦截，并且能在侧边栏历史里看到这条 is_success 为 0 的记录。左边是界面布局：下方三块分别展示生成的 SQL、结果表格和自然语言回答，右侧是运行状态和历史。为了防止教室网络问题，我准备了手机热点和一组成功截图做兜底。");

// ================= S9 长尾分布 =================
s = p.addSlide(); s.background = { color: BG };
kicker(s, "08 · 数据设计"); title(s, "长尾分布：让“播放量排名”有区分度");
s.addChart(p.charts.BAR, [
  { name: "均匀随机分布", labels: ["第 1 名", "第 2 名", "第 3 名", "第 4 名", "第 5 名"], values: [20, 19, 19, 19, 19] },
  { name: "对数正态热度分布", labels: ["第 1 名", "第 2 名", "第 3 名", "第 4 名", "第 5 名"], values: [194, 160, 130, 112, 106] },
], {
  x: 0.6, y: 1.55, w: 7.2, h: 4.75, barDir: "col", barGapWidthPct: 60,
  chartColors: ["C9C2E8", "E8A33D"],
  chartArea: { fill: { color: "FFFFFF" } },
  catAxisLabelColor: MUTED, catAxisLabelFontFace: F, catAxisLabelFontSize: 12,
  valAxisLabelColor: MUTED, valAxisLabelFontFace: F, valAxisLabelFontSize: 12,
  valGridLine: { color: "EDEBF4", size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: TEXT, dataLabelFontFace: F, dataLabelFontSize: 12,
  showLegend: true, legendPos: "t", legendFontFace: F, legendFontSize: 12.5, legendColor: TEXT,
  showTitle: false,
});
const pts9 = [
  ["问题", "均匀随机：播放量挤在均值 ±5，前五名全是并列，排名没有信息量"],
  ["方案", "对数正态热度：头部歌曲 194 次、长尾歌曲个位数，贴近真实产品"],
  ["约束", "数据量保持 5000 条（任务书要求）——只改分布，不改数量"],
];
pts9.forEach(([t, d], i) => {
  s.addText([
    { text: t, options: { bold: true, fontSize: 15.5, color: i === 1 ? "9A6A12" : PRIMARY_DK, breakLine: true } },
    { text: d, options: { fontSize: 12.5, color: MUTED } },
  ], { x: 8.25, y: 1.75 + i * 1.55, w: 4.45, h: 1.4, fontFace: F, lineSpacingMultiple: 1.18, margin: 0 });
});
s.addText("数据来源：music_query 库实测查询（data/import_data.py 生成）", { x: 0.6, y: 6.85, w: 7.2, h: 0.3, fontSize: 12, color: MUTED, fontFace: F, margin: 0 });
badge(s, 9);
s.addNotes("这页讲数据设计的一个亮点。最初的测试数据是完全均匀随机生成的，五百首歌分五千次播放，每首平均十次，前五名全都挤在二十次左右并列——排名本身没有信息量。真实音乐产品的播放量是长尾的：少数爆款占大头，大量歌曲只有个位数播放。所以我改用对数正态分布模拟热度，头部歌曲将近两百次，长尾歌曲个位数。注意数据量仍然是任务书要求的 5000 条，我们改的只是分布，不是数量。");

// ================= S10 总结（深色收尾） =================
s = p.addSlide(); s.background = { color: BG_DARK };
s.addText("谢谢聆听", { x: 0.7, y: 0.95, w: 6.5, h: 0.95, fontSize: 44, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
s.addText("请各位老师批评指正", { x: 0.7, y: 1.95, w: 6.5, h: 0.45, fontSize: 17, color: D_MUTED, fontFace: F, margin: 0 });
const stats10 = [["6", "张表 · 三范式设计"], ["4", "个索引 · EXPLAIN 实证"], ["3", "道安全防线"], ["2", "次失败自动重试"]];
stats10.forEach(([n, l], i) => {
  const x = 0.7 + i * 3.05;
  s.addText(n, { x, y: 2.85, w: 2.7, h: 0.85, fontSize: 44, bold: true, color: ACCENT, fontFace: F, margin: 0 });
  s.addText(l, { x, y: 3.72, w: 2.8, h: 0.4, fontSize: 13.5, color: D_MUTED, fontFace: F, margin: 0 });
});
s.addText("后续改进", { x: 0.7, y: 4.75, w: 4, h: 0.4, fontSize: 14.5, bold: true, color: ACCENT, fontFace: F, margin: 0 });
s.addText([
  { text: "① 应用账号只授 SELECT 权限，把安全防线下沉到数据库层", options: { breakLine: true } },
  { text: "② 构建 few-shot 示例库，提升复杂问句的 SQL 生成准确率", options: { breakLine: true } },
  { text: "③ 引入结果缓存与连接池，支撑更高并发查询", options: {} },
], { x: 0.7, y: 5.2, w: 11.9, h: 1.5, fontSize: 15, color: "E8E4F2", fontFace: F, lineSpacingMultiple: 1.55, margin: 0 });
[[10.6, 5.05, 2.2, "2E2650"], [11.0, 5.45, 1.6, "38305C"]].forEach(([x, y, d, c]) => {
  s.addShape(p.shapes.OVAL, { x, y, w: d, h: d, line: { color: c, width: 1.25 } });
});
s.addShape(p.shapes.OVAL, { x: 11.65, y: 6.1, w: 0.3, h: 0.3, fill: { color: ACCENT } });
s.addNotes("最后总结：项目交付了 6 张表的完整数据库设计、4 个经 EXPLAIN 实证的索引、三道安全防线和最多两次的失败自动重试。改进方向也想清楚了：把应用账号限制成只读、用 few-shot 示例提升复杂问句的准确率、再加缓存和连接池。我的汇报到此结束，谢谢各位老师。");

p.writeFile({ fileName: "E:/musicquery-agent/MusicQuery-Agent-答辩.pptx" }).then(() => console.log("PPTX_DONE"));
