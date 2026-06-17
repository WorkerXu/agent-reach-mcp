<h1 align="center">👁️ Agent Reach</h1>

<p align="center">
  <strong>وصول إلى الإنترنت بنقرة واحدة لوكلاء الذكاء الاصطناعي</strong>
</p>

<p align="center">
  طرق الوصول الأكثر استقراراً، يتم اختيارها وتثبيتها وتشخيصها لك — طرق الوصول تتطور، أنت لا تقلق
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://github.com/Panniantong/agent-reach/stargazers"><img src="https://img.shields.io/github/stars/Panniantong/agent-reach?style=for-the-badge" alt="GitHub Stars"></a>
  <a href="https://trendshift.io/repositories/24387"><img src="https://trendshift.io/api/badge/repositories/24387" alt="Trendshift GitHub Trending #1 Repository of the Day"></a>
</p>

<p align="center">
  <a href="../README.md">English</a> · <a href="README_ja.md">日本語</a> · <a href="README_ko.md">한국어</a> · <a href="#quick-start">البدء السريع</a> · <a href="#supported-platforms">المنصات المدعومة</a> · <a href="#design-philosophy">فلسفة التصميم</a>
</p>

---

## لماذا Agent Reach؟

وكلاء الذكاء الاصطناعي يمكنهم بالفعل كتابة الكود وتحرير المستندات وإدارة المشاريع — لكن اطلب منهم العثور على شيء عبر الإنترنت، ولن يستطيعوا:

- 📺 «تفقّد ما يقوله هذا الفيديو التعليمي على YouTube» → **لا يستطيع**، لا يمكنه الحصول على الترجمة
- 🐦 «ابحث عما يقوله الناس عن هذا المنتج على Twitter» → **لا يستطيع**، واجهة Twitter API تتطلب الدفع
- 📖 «اذهب لتفقّد Reddit إن كان أحدٌ قد واجه نفس المشكلة» → **ممنوع 403**، تم رفض عنوان IP للخادم
- 📕 «تفقّد مراجعات هذا المنتج على XiaoHongShu» → **لا يمكن فتحه**، يجب تسجيل الدخول للمشاهدة
- 📺 «هناك فيديو تقني على Bilibili، لخّصه» → **لا يمكن الحصول عليه**، أدوات التحميل العامة محجوبة بالكامل من قبل نظام مكافحة السحّب في Bilibili
- 🔍 «ابحث عبر الإنترنت عن أحدث مقارنة لأطر عمل LLM» → **لا توجد أداة بحث جيدة**، إما مدفوعة أو منخفضة الجودة
- 🌐 «تفقّد محتوى صفحة الويب هذه» → **يعيد فوضى من علامات HTML**، غير قابل للقراءة
- 📦 «ما موضوع هذا المستودع على GitHub؟ ماذا تقول الـ Issues؟» → يمكن استخدامه، لكن إعداد المصادقة مؤلم
- 📡 «اشترك في خلاصات RSS هذه وأبلغني بالتحديثات» → تحتاج إلى تثبيت مكتبات وكتابة كود

**هذه الأمور ليست صعبة التنفيذ، لكنها تتطلب تكويناً مملاً**

كل منصة لها حواجزها الخاصة — واجهات برمجية مدفوعة، حظر يجب تجاوزه، حسابات يجب تسجيل الدخول إليها، بيانات يجب تنظيفها. عليك التعامل مع كل منها على حدة، تثبيت أدوات، تعديل إعدادات. مجرد جعل الوكيل يقرأ Twitter يستغرق نصف يوم.

**Agent Reach يحوّل هذا إلى جملة واحدة:**

```
Install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

انسخ ذلك إلى وكيلك، وبعد دقائق يمكنه قراءة Twitter، والبحث في Reddit، ومشاهدة YouTube، وتصفح XiaoHongShu.

**مثبت بالفعل؟ التحديث أيضًا جملة واحدة:**

```
Update Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

> ⭐ **قم بتصنيف هذا المشروع بالنجمة** — سنتابع تغيير المنصات باستمرار ونضيف قنوات جديدة. لست مضطراً للمراقبة بنفسك — عندما تحظرنا المنصات، نصلحها؛ عندما تظهر قنوات جديدة، نضيفها.

### ✅ قبل أن تستخدمه، قد ترغب في معرفة

| | |
|---|---|
| 💰 **مجاني تماماً** | جميع الأدوات مفتوحة المصدر، جميع الـ APIs مجانية. التكلفة الوحيدة المحتملة هي بروكسي خادم ($1/شهر)، غير مطلوبة على الأجهزة المحلية |
| 🔒 **الخصوصية والأمان** | ملفات تعريف الارتباط (Cookies) موجودة فقط على جهازك المحلي، ولا يتم تحميلها أو مشاركتها أبداً. الكود مفتوح المصدر بالكامل، يمكن مراجعته في أي وقت |
| 🔄 **تطوّر مستمر** | كل منصة تستخدم نظام توجيه متعدد الخلفيات «أساسي + احتياطي». عندما تفشل طريقة وصول، ننتقل إلى التالية، بشكل شفاف بالنسبة لك (مثال يونيو 2026: yt-dlp محظور من Bilibili → التحويل إلى bili-cli، دون أي تدخل من المستخدم) |
| 🤖 **متوافق مع جميع الوكلاء** | Claude Code، OpenClaw، Cursor، Windsurf… أي وكيل يمكنه تشغيل أوامر الطرفية يعمل |
| 🩺 **تشخيص مدمج** | `agent-reach doctor` — أمر واحد يخبرك بما يعمل وما لا يعمل وكيفية إصلاحه |

---

## المنصات المدعومة

| المنصة | جاهزة فوراً | تتطلب إعدادات | كيفية الإعداد |
|------|---------|-----------|-------|
| 🌐 **الويب** | قراءة أي صفحة ويب | — | لا حاجة لإعدادات |
| 📺 **YouTube** | استخراج الترجمة + البحث عن الفيديو | — | لا حاجة لإعدادات |
| 📡 **RSS** | قراءة أي خلاصة RSS/Atom | — | لا حاجة لإعدادات |
| 🔍 **البحث في الويب** | — | بحث دلالي كامل على الويب | إعداد تلقائي (دمج MCP، مجاني بدون مفتاح) |
| 📦 **GitHub** | قراءة المستودعات العامة + البحث | المستودعات الخاصة، Issues/PRs، Fork | أخبر وكيلك «اضبط GitHub لي» |
| 🐦 **Twitter/X** | قراءة التغريدات الفردية | بحث التغريدات، تصفح الجدول الزمني، قراءة السلاسل | أخبر وكيلك «اضبط Twitter لي» |
| 📺 **Bilibili** | بحث + تفاصيل الفيديو (bili-cli، بدون تسجيل دخول) | الترجمة (OpenCLI) | أخبر وكيلك «اضبط Bilibili لي» |
| 📖 **Reddit** | — (لا يوجد مسار بدون إعدادات: الـ API المجهول محظور) | بحث + قراءة المنشورات والتعليقات | سطح المكتب: ثبّت OpenCLI (يستخدم جلسة المتصفح)؛ أو rdt-cli + Cookie |
| 📕 **XiaoHongShu** | — | بحث، قراءة، تعليق | سطح المكتب: ثبّت OpenCLI (يعمل إذا كنت تتصفح XiaoHongShu)؛ خادم: xiaohongshu-mcp مع تسجيل الدخول عبر QR |
| 💼 **LinkedIn** | Jina Reader يقرأ الصفحات العامة | تفاصيل الملف الشخصي، صفحات الشركات، البحث عن وظائف | أخبر وكيلك «اضبط LinkedIn لي» |
| 💻 **V2EX** | المواضيع الساخنة، منشورات الأقسام، تفاصيل الموضوع+الردود، معلومات المستخدم | — | لا حاجة لإعدادات |
| 📈 **Xueqiu** | أسعار الأسهم، بحث الأسهم، المنشورات الساخنة، تصنيفات الأسهم الساخنة | — | أخبر وكيلك «اضبط Xueqiu لي» |
| 🎙️ **Xiaoyuzhou Podcast** | — | نص البودكاست من الصوت (نسخ Whisper، مفتاح مجاني) | أخبر وكيلك «اضبط Xiaoyuzhou لي» |

> **لا تعرف كيفية الإعداد؟ لا حاجة لمراجعة المستندات.** فقط أخبر وكيلك «اضبط XXX لي» — إنه يعرف ما هو مطلوب وسيرشدك خطوة بخطوة.
>
> 🍪 للمنصات التي تتطلب ملفات تعريف الارتباط (Twitter، XiaoHongShu، إلخ)، **يُفضّل** استخدام إضافة كروم [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) لتصدير الـ Cookies، ثم إرسالها إلى وكيلك. سير عمل موحد: تسجيل الدخول في المتصفح → تصدير Cookie-Editor → إرسال إلى الوكيل. أبسط وأكثر موثوقية من مسح رمز QR.
>
> 🔒 تبقى الـ Cookies على جهازك المحلي فقط، ولا يتم تحميلها أو مشاركتها أبداً. الكود مفتوح المصدر بالكامل، يمكن مراجعته في أي وقت.
> 💻 الأجهزة المحلية لا تحتاج إلى بروكسي. البروكسي مطلوب فقط عند النشر على خادم (~$1/شهر).

---

## البداية السريعة

> ⚠️ **مستخدمو OpenClaw: تأكد من تفعيل صلاحية التنفيذ أولاً**
>
> يعتمد Agent Reach على قدرة وكيلك على تنفيذ أوامر الطرفية (`pip install`، `mcporter`، `twitter`، إلخ). إذا كان OpenClaw الخاص بك يستخدم ملف تعريف `messaging` الافتراضي للأدوات، فلن يتمكن الوكيل من تشغيل الأوامر. **قم بتفعيل صلاحية التنفيذ قبل التثبيت**:
>
> ```bash
> openclaw config set tools.profile "coding"
> ```
> أو اضبط `"tools": { "profile": "coding" }` في ملف `~/.openclaw/openclaw.json`.
> ثم أعد تشغيل Gateway (`openclaw gateway restart`) وابدأ محادثة جديدة. المنصات الأخرى (Claude Code، Cursor، Windsurf، إلخ) غير متأثرة.

انسخ هذا إلى وكيل الذكاء الاصطناعي الخاص بك (Claude Code، OpenClaw، Cursor، إلخ):

```
Install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

هذا كل شيء. سيتولى الوكيل الباقي.

> 🔄 **مثبت بالفعل؟** التحديث أيضًا جملة واحدة:
> ```
> Update Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
> ```

> 🛡️ **قلق بشأن الأمان؟** استخدم الوضع الآمن — لن يقوم بتثبيت حزم النظام تلقائياً، فقط يخبرك بما هو مطلوب:
> ```
> Install Agent Reach (safe mode): https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> Use the --safe flag when installing
> ```

<details>
<summary>ماذا يفعل؟ (اضغط للتوسيع)</summary>

1. **تثبيت أداة CLI** — `pip install` لأمر `agent-reach` (يضم yt-dlp، feedparser)
2. **تثبيت البنية التحتية للنظام** — كشف وتثبيت Node.js، gh CLI، mcporter تلقائياً
3. **إعداد محرك البحث** — ربط Exa عبر MCP (مجاني، بدون مفتاح API)
4. **كشف البيئة** — تحديد ما إذا كان جهازاً محلياً أو خادماً، وتقديم توصيات إعدادات مناسبة
5. **تسجيل SKILL.md** — تثبيت دليل الاستخدام في دليل مهارات الوكيل. عندما يواجه الوكيل مهاماً مثل «ابحث في الويب»، «ابحث في Twitter»، أو «شاهد فيديو»، فإنه يعرف تلقائياً أي أداة خارجية يستدعيها
6. **اسأل إن كنت تريد المزيد** — بشكل افتراضي، يُفعّل 6 قنوات بدون إعدادات. بالنسبة لـ XiaoHongShu، Twitter، Reddit (التي تتطلب تسجيل دخول)، سيعرض الوكيل قائمة ليسألك أي منها تريد

بعد التثبيت، `agent-reach doctor` — أمر واحد يخبرك بحالة كل قناة وأي مسار خلفي يُستخدم حالياً.
</details>

---

## جاهز للاستخدام

لا حاجة لإعدادات، فقط أخبر وكيلك:

- «تفقّد هذا الرابط» → `curl https://r.jina.ai/URL` يقرأ أي صفحة ويب
- «ما الذي يفعله هذا المستودع على GitHub» → `gh repo view owner/repo`
- «ماذا يقول هذا الفيديو على YouTube» → `yt-dlp` يستخرج الترجمة
- «ابحث في Bilibili عن دروس AI» → `bili search` (بدون تسجيل دخول)
- «ابحث في الويب عن مقارنة أطر عمل LLM» → بحث دلالي عبر Exa
- «اشترك في خلاصة RSS هذه» → `feedparser` يحللها

**لا حاجة لحفظ الأوامر.** بعد قراءة SKILL.md، يعرف الوكيل أي أداة يستدعيها. للمنصات التي تتطلب تسجيل دخول (XiaoHongShu، Twitter، Reddit)، فقط أخبر وكيلك «اضبط XXX لي» لفتحها.

---

## النطاق: قراءة المحتوى مقابل التفاعل مع صفحات الويب

بعض المهام تتجاوز «القراءة»: عمليات على صفحات ويب بعد تسجيل الدخول، تقديم نماذج، عزل حسابات متعددة، جلسات متصفح متوازية، وتدخل بشري للخطوات عالية الاحتكاك مثل تسجيل الدخول وCAPTCHA ومكافحة البوتات في سير العمل الآلي. لهذه السيناريوهات «العملية»، فكر في الاقتران بأدوات أتمتة المتصفح مثل [BrowserAct](https://www.browseract.ai/Agent) — أكثر من 30 مهارة منصة مبنية مسبقاً تدعم Claude Code / OpenClaw / Cursor وغيرها من الوكلاء الرئيسيين.

---

## فلسفة التصميم

**Agent Reach هو طبقة قدرة، ليس مجرد أداة أخرى.**

يقع مستوى واحداً فوق أي تنفيذ ملموس — مسؤول عن **الاختيار، التثبيت، التشخيص، والتوجيه**، وليس عن القراءة الأساسية نفسها. القراءة تتم عن طريق الوكيل الذي يستدعي الأدوات الخارجية مباشرة، بدون طبقة تغليف.

عند إعداد وكيل جديد، تحتاج دائماً إلى قضاء وقت في البحث عن الأدوات، تثبيت التبعيات، وتعديل الإعدادات — ماذا تستخدم لـ Twitter؟ كيف تسجل دخولك إلى Reddit؟ واجهة XiaoHongShu CLI توقفت عن التحديث، بماذا تستبدلها؟ عليك أن تمر بكل هذا من جديد في كل مرة. ما يفعله Agent Reach بسيط: **طرق الوصول الأكثر استقراراً، يتم اختيارها وتثبيتها وتشخيصها لك. طرق الوصول تتطور (في مارس 2026، توقفت مجموعة من أدوات CLI أحادية المنصة عن التحديث؛ قمنا بتبديل المسارات)، أنت لا تقلق.**

### 🔌 كل منصة = قائمة خلفيات مرتبة مع أساسي واحتياطي

تبديل طرق الوصول = إعادة ترتيب القائمة، ليس إعادة كتابة الكود. `agent-reach doctor` يخبرك **أي خلفية تستخدمها كل منصة حالياً**.

```
channels/
├── web.py          → Jina Reader
├── twitter.py      → twitter-cli ▸ OpenCLI ▸ bird
├── youtube.py      → yt-dlp
├── github.py       → gh CLI
├── bilibili.py     → bili-cli ▸ OpenCLI ▸ Search API (yt-dlp محظور من Bilibili لمكافحة السحّب، متقاعد)
├── reddit.py       → OpenCLI ▸ rdt-cli (لا يوجد مسار بدون إعدادات، يجب تسجيل الدخول)
├── xiaohongshu.py  → OpenCLI ▸ xiaohongshu-mcp ▸ xhs-cli
├── linkedin.py     → linkedin-mcp ▸ Jina Reader
├── rss.py          → feedparser
├── exa_search.py   → Exa عبر mcporter
└── __init__.py     → سجل القنوات (يستخدمه doctor)
```

كل ملف قناة **يختبر فعلياً** الخلفيات المرشحة بالترتيب (ليس فقط التحقق من وجود الأمر)؛ يتم اختيار أول خلفية تعمل بكامل طاقتها. الخلفيات المعطلة تحصل على وصفة إصلاح. القراءة والبحث الفعليين يتمان بواسطة الوكيل الذي يستدعي الأدوات الخارجية مباشرة.

### الاختيارات الحالية

| السيناريو | الأساسي | الاحتياطي | لماذا هذا الاختيار |
|------|------|------|-----------|
| قراءة صفحات الويب | [Jina Reader](https://github.com/jina-ai/reader) | — | مجاني، بدون مفتاح API |
| قراءة التغريدات | [twitter-cli](https://github.com/public-clis/twitter-cli) | [OpenCLI](https://github.com/jackwener/opencli) | استقرار البحث مُختبر؛ OpenCLI يستخدم جلسة تسجيل دخول المتصفح كخيار احتياطي |
| Reddit | [OpenCLI](https://github.com/jackwener/opencli) (سطح المكتب) | [rdt-cli](https://github.com/public-clis/rdt-cli) | الـ API المجهول محظور، الـ API الرسمي بالموافقة فقط — فقط مسار تسجيل الدخول بقي متاحاً |
| ترجمة YouTube + بحث | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | — | 154K نجمة، لا يزال الأفضل لـ YouTube (ملاحظة: لم يعد يُستخدم لـ Bilibili) |
| Bilibili | [bili-cli](https://github.com/public-clis/bilibili-cli) | OpenCLI ▸ Search API | yt-dlp محظور من Bilibili بـ 412 (مُختبر يونيو 2026)، bili-cli يعمل بدون تسجيل دخول |
| البحث في الويب | [Exa](https://exa.ai) عبر [mcporter](https://github.com/nicobailon/mcporter) | — | بحث دلالي بالذكاء الاصطناعي، دمج MCP، بدون مفتاح |
| GitHub | [gh CLI](https://cli.github.com) | — | أداة رسمية، إمكانيات API كاملة بعد المصادقة |
| قراءة RSS | [feedparser](https://github.com/kurtmckee/feedparser) | — | معيار بيئة Python |
| XiaoHongShu | [OpenCLI](https://github.com/jackwener/opencli) (سطح المكتب) | [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (خادم) ▸ xhs-cli | مطور xhs-cli انتقل إلى OpenCLI (24K نجمة)؛ جلسة متصفح، بدون احتكاك |
| LinkedIn | [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) | Jina Reader | خدمة MCP، أتمتة متصفح |

> 📌 هذه كلها «اختيارات حالية»، تُراجع دورياً بناءً على اختبارات أجهزة حقيقية. عندما يفشل مسار، ننتقل إلى التالي — `agent-reach doctor` يخبرك دائماً أي مسار يُستخدم حالياً.

---

## الأمان

يركز Agent Reach على الأمان في تصميمه:

| الإجراء | الوصف |
|------|------|
| 🔒 **تخزين بيانات الاعتماد محلياً** | الـ Cookies والرموز موجودة فقط على جهازك المحلي في `~/.agent-reach/config.yaml`، صلاحيات الملف 600 (قراءة/كتابة للمالك فقط)، لا يتم تحميلها أو مشاركتها أبداً |
| 🛡️ **الوضع الآمن** | `agent-reach install --safe` لا يعدّل النظام تلقائياً، فقط يسرد ما هو مطلوب، تاركاً لك القرار بشأن ما تريد تثبيته |
| 👀 **مفتوح المصدر بالكامل** | الكود شفاف ويمكن مراجعته في أي وقت. جميع الأدوات التابعة هي أيضاً مشاريع مفتوحة المصدر |
| 🔍 **التجربة الجافة** | `agent-reach install --dry-run` يعاين جميع العمليات دون إجراء أي تغييرات |
| 🧩 **بنية قابلة للتبديل** | لا تثق بمكون؟ استبدل ملف القناة المقابل دون التأثير على أي شيء آخر |

### 🍪 نصائح أمان ملفات تعريف الارتباط (Cookies)

> ⚠️ **تذكير بخطر حظر الحساب:** المنصات التي تستخدم الـ Cookies لتسجيل الدخول (Twitter، XiaoHongShu، إلخ) عند الوصول إليها عبر البرامج النصية/API **تحمل خطر اكتشافها وحظرها من قبل المنصة**. يُرجى استخدام **حساب ثانوي مخصص**، وليس حسابك الرئيسي.

للمنصات التي تتطلب الـ Cookies (Twitter، XiaoHongShu)، نوصي باستخدام **حساب ثانوي مخصص** بدلاً من حسابك الرئيسي. سببين:
1. **خطر حظر الحساب** — قد تكتشف المنصات أنماط استدعاء غير قادمة من متصفح، مما يؤدي إلى تقييد الحساب أو حظره
2. **خطر أمني** — تمنح الـ Cookies وصولاً كاملاً لتسجيل الدخول؛ استخدام حساب ثانوي يحد من نطاق الضرر إذا تم اختراق بيانات الاعتماد

### 📦 طرق التثبيت

| الطريقة | الأمر | الأفضل لـ |
|------|------|---------|
| بنقرة واحدة تلقائي (افتراضي) | `agent-reach install --env=auto` | الكمبيوتر الشخصي، بيئة التطوير |
| الوضع الآمن | `agent-reach install --env=auto --safe` | خوادم الإنتاج، الأجهزة متعددة المستخدمين |
| معاينة فقط | `agent-reach install --env=auto --dry-run` | لرؤية ما سيفعله أولاً |

### 🗑️ إلغاء التثبيت

```bash
agent-reach uninstall
```

هذا يزيل: `~/.agent-reach/` (بما في ذلك جميع الرموز/الـ Cookies)، جميع ملفات مهارات الوكيل، وإعدادات MCP لـ mcporter.

```bash
# معاينة فقط، لا يحذف فعلياً
agent-reach uninstall --dry-run

# إزالة ملفات المهارات فقط، الاحتفاظ بإعدادات الرموز (لإعادة التثبيت)
agent-reach uninstall --keep-config
```

لإلغاء تثبيت حزمة Python نفسها: `pip uninstall agent-reach`

---

## المساهمة

هذا المشروع تم إنشاؤه بالكامل عن طريق الـ vibe coding 🎸 قد يكون هناك بعض النواقص، وإذا واجهت أي مشكلة فالرجاء التسامح. أي خلل، ارفع [Issue](https://github.com/Panniantong/agent-reach/issues) وسأقوم بإصلاحه في أقرب وقت.

**تريد قناة جديدة؟** ارفع Issue وأخبرنا، أو قدم PR بنفسك.

**تريد الإضافة محلياً؟** اجعل وكيلك يستنسخ المشروع ويعدّل عليه، كل قناة هي ملف مستقل، إضافتها بسيطة جداً.

[PRs](https://github.com/Panniantong/agent-reach/pulls) مرحب بها دائماً!

---

## ⭐ لماذا تستحق النجمة

هذا المشروع أستخدمه شخصياً يومياً، لذا سأستمر في صيانته.

- إذا كانت هناك احتياجات جديدة أو قنوات يطلبها الجميع، سأضيفها تباعاً
- سأحرص على أن تكون كل قناة **قابلة للاستخدام، جيدة، ومجانية**
- إذا غيّرت المنصات نظام مكافحة السحّب أو الـ APIs، سأجد حلاً

أساهم في بناء البنية التحتية للويب 4.0.

ضع نجمة ⭐، لتجده عندما تحتاجه في المرة القادمة.

---

## الأسئلة الشائعة / FAQ

<details>
<summary><strong>كيف يبحث وكيل الذكاء الاصطناعي في Twitter / X؟ لا أريد دفع رسوم API</strong></summary>

يستخدم Agent Reach [twitter-cli](https://github.com/public-clis/twitter-cli) للوصول إلى Twitter عبر مصادقة الـ Cookies، مجاني تماماً. التثبيت: `pipx install twitter-cli`، تأكد من أن المتصفح قد سجل الدخول إلى x.com، وبعدها يمكن للوكيل استخدام `twitter search "كلمة مفتاحية"` للبحث و`twitter tweet URL` لقراءة التغريدة.
</details>

<details>
<summary><strong>كيف أبحث في Reddit مع وكيل AI مجاناً (بدون API)؟</strong></summary>

يستخدم Agent Reach OpenCLI مع جلسة المتصفح — بدون رسوم API. على سطح المكتب: ثبّت OpenCLI (يتضمنه `agent-reach install`)، تأكد من أن متصفحك قد سجل الدخول إلى reddit.com، ثم `opencli reddit search "استعلام"`. الخيار البديل: [rdt-cli](https://github.com/public-clis/rdt-cli) مع `rdt login`.
</details>

<details>
<summary><strong>ماذا أفعل عندما يعيد Reddit خطأ 403؟</strong></summary>

جميع عمليات الوصول إلى Reddit تتطلب حالة تسجيل دخول (الواجهات المجهولة محجوبة بالكامل، الـ API الرسمي يتطلب موافقة بشرية). سطح المكتب الخيار الأول هو **OpenCLI**: بمجرد تسجيل الدخول إلى reddit.com في المتصفح يمكنك مباشرة استخدام `opencli reddit search "كلمة مفتاحية"`. الخيار البديل [rdt-cli](https://github.com/public-clis/rdt-cli): `pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'` (نفس الإصدار المثبت في الكود، PyPI متأخر)، ثم `rdt login`. الوصول إلى Reddit من الشبكات في الصين القارية يحتاج إلى بروكسي.
</details>

<details>
<summary><strong>كيف أحصل على نصوص فيديوهات YouTube للذكاء الاصطناعي؟</strong></summary>

`yt-dlp --dump-json "https://youtube.com/watch?v=xxx"` يستخرج بيانات الفيديو؛ `yt-dlp --write-sub --skip-download "URL"` يستخرج الترجمة. يستخدم yt-dlp في الخلفية، يدعم لغات متعددة. لا حاجة لمفتاح API.
</details>

<details>
<summary><strong>كيف أجعل وكيل AI يقرأ XiaoHongShu؟</strong></summary>

على سطح المكتب الخيار الأول هو **OpenCLI** (`agent-reach install --channels opencli`) — يعيد استخدام جلسة تسجيل الدخول من متصفحك، إذا كنت تتصفح XiaoHongShu عادة فهو يعمل مباشرة، بدون إعدادات؛ بعد التثبيت، أضف الإضافة من متجر Chrome بنقرة واحدة. بعدها يستخدم الوكيل `opencli xiaohongshu search "كلمة مفتاحية"` للبحث و`opencli xiaohongshu note URL` لقراءة الملاحظات. على الخادم استخدم [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (مزود بمتصفح بدون واجهة، تسجيل دخول بمسح QR). المستخدمون القدامى الذين ثبّتوا xhs-cli سابقاً لن يتأثروا، ولا يزال خياراً احتياطياً (التحديثات توقفت منذ مارس 2026، لا نوصي بالتثبيت الجديد).
</details>

<details>
<summary><strong>هل يتوافق مع Claude Code / Cursor / OpenClaw / Windsurf؟</strong></summary>

نعم! Agent Reach هو أداة تثبيت + إعدادات — أي وكيل برمجة ذكاء اصطناعي يمكنه تشغيل أوامر الطرفية يمكنه استخدامه. يعمل مع Claude Code، Cursor، OpenClaw، Windsurf، Codex، والمزيد. فقط `pip install agent-reach`، ثم شغّل `agent-reach install`، ويستطيع الوكيل البدء في استخدام الأدوات الخارجية فوراً.

**ملاحظة OpenClaw:** إذا كان OpenClaw الخاص بك يستخدم ملف تعريف الأدوات `messaging` الافتراضي، لن يتمكن الوكيل من تشغيل أوامر الطرفية. فعّل التنفيذ أولاً: `openclaw config set tools.profile "coding"` (أو اضبط `"tools": { "profile": "coding" }` في `~/.openclaw/openclaw.json`)، ثم أعد تشغيل Gateway وابدأ محادثة جديدة قبل التثبيت.
</details>

<details>
<summary><strong>هل هذا مجاني؟ هل هناك أي تكاليف API؟</strong></summary>

مجاني 100%. جميع الخلفيات هي أدوات مفتوحة المصدر (OpenCLI، twitter-cli، bili-cli، rdt-cli، yt-dlp، Jina Reader، Exa، xiaohongshu-mcp، إلخ) ولا تتطلب مفاتيح API مدفوعة. التكلفة الاختيارية الوحيدة هي بروكسي سكني (~$1/شهر) إذا كانت شبكتك تحظر Reddit/Twitter (مثلاً الصين القارية).
</details>

---

## الشكر والتقدير

[OpenCLI](https://github.com/jackwener/opencli) · [twitter-cli](https://github.com/public-clis/twitter-cli) · [rdt-cli](https://github.com/public-clis/rdt-cli) · [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) · [xhs-cli](https://github.com/jackwener/xiaohongshu-cli) · [bili-cli](https://github.com/public-clis/bilibili-cli) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Jina Reader](https://github.com/jina-ai/reader) · [Exa](https://exa.ai) · [mcporter](https://github.com/nicobailon/mcporter) · [feedparser](https://github.com/kurtmckee/feedparser) · [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server)

## التواصل

- 📧 **البريد الإلكتروني:** pnt01@foxmail.com
- 🐦 **Twitter/X:** [@Neo_Reidlab](https://x.com/Neo_Reidlab)

للتواصل أو التعاون، أضف WeChat وسأضمك إلى مجموعة النقاش:

<p align="center">
  <img src="docs/wechat-group-qr.jpg" width="280" alt="رمز WeChat QR">
</p>

> للإبلاغ عن الأخطاء وطلبات الميزات، يُرجى استخدام [GitHub Issues](https://github.com/Panniantong/Agent-Reach/issues)، فهي أسهل للمتابعة.

## الرخصة

[MIT](LICENSE)

## روابط صديقة

[Tencent Cloud OpenClaw](https://www.tencentcloud.com/act/pro/intl-openclaw?referral_code=G76Y819A&lang=zh&pg=) — انشر OpenClaw الشامل على Tencent Cloud Lighthouse في ثوانٍ، واربطه بـ Agent Reach بسلاسة عبر المحادثة، لتمنح وكيلك إمكانيات الإنترنت بنقرة واحدة.

[مرآة AtomGit](https://atomgit.com/qq_51337814/Agent-Reach) — مرآة مزامنة Agent Reach على AtomGit، لتسهيل الوصول والاستنساخ داخل الصين.

## تاريخ النجمة

[![Star History Chart](https://api.star-history.com/svg?repos=Panniantong/Agent-Reach&type=Date&v=20260309)](https://star-history.com/#Panniantong/Agent-Reach&Date)
