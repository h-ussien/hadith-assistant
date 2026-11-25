/* ============================================================
   Dalil-style research assistant UI — vanilla JS
   Search: Shamela MCP + Dorar.net + local catalog. Accounts: role-aware local login.
   ============================================================ */

const I18N = {
  ar: {
    pageTitle: 'دليل الأبحاث الحديثية — مساعد البحث والتوثيق',
    brandTitle: 'دليل الأبحاث الحديثية',
    brandSubtitle: 'الاسترجاع والتوثيق لنصوص أحاديث الأحكام والنقولات',
    mainNav: 'التنقل الرئيسي', navAsk: 'اسأل', navWorkspace: 'مساحة العمل',
    navHistory: 'السجل', navUsers: 'المستخدمون', navSources: 'المصادر', navAdmin: 'الإدارة',
    themeToggle: 'تبديل المظهر', openMenu: 'فتح القائمة', signIn: 'دخول',
    chatTitle: 'مساعد البحث في الأحاديث والنقولات',
    chatSubtitle: 'استرجاع النصوص ومصادرها من المكتبة الشاملة أو الدرر السنية أو فهارسك المحلية — دون توليد فتاوى أو أحكام.',
    queryLabel: 'اكتب نص الحديث أو النقل للبحث',
    queryPlaceholder: 'اكتب النص هنا… (Enter للإرسال)',
    scopeLabel: 'نطاق البحث', scopeShamela: 'المكتبة الشاملة',
    scopeDorar: 'الدرر السنية (dorar.net)',
    scopeHadith: 'الأحاديث (الفهرس المحلي)', scopeQuote: 'النقولات (الفهرس المحلي)',
    scopeAll: 'كل المصادر (المحلي)',
    methodNote: 'النتائج من أربعة كتب فقط: صحيح البخاري، صحيح مسلم، سنن أبي داود، جامع الترمذي — استرجاع نصوص بلا فتاوى.',
    methodNoteDorar: 'نتائج الدرر السنية تعرض النص والمصدر وخلاصة حكم المحدث — استرجاع بلا فتاوى.',
    methodNoteLocal: 'البحث في الفهارس التي تستوردها بنفسك فقط — استرجاع بلا فتاوى.',
    send: 'إرسال', emptyTitle: 'كلُّ نصٍّ بمصدره.',
    emptyHint: 'اكتب مقطعًا من حديث أو نقل، وستظهر النصوص المطابقة من المكتبة الشاملة أو الدرر السنية أو فهارسك مع المصدر ورابطه.',
    booksTitle: 'مساحة العمل',
    booksSubtitle: 'ابحث في المقتطفات المستوردة من كتبك، وأدر فهارسك المحلية.',
    bookSearchTitle: 'البحث في كتبي المستوردة',
    bookSearchHint: 'يبحث هذا الفهرس في النقولات التي تستوردها بنفسك. لا توجد مكتبة كاملة أو نسخة «الشاملة» مرفقة، والسجلات المستوردة لا تُوثَّق آليًا.',
    textKind: 'نوع النص', wordHadith: 'حديث', wordQuote: 'نقل كلاسيكي',
    textOrExcerpt: 'النص أو المقطع', bookQueryPlaceholder: 'أدخل جزءًا من الحديث أو النص',
    searchMyBooks: 'ابحث في كتبي', importTitle: 'استيراد فهرس كتاب', adminOnly: 'للمدير فقط',
    importHint: 'ارفع ملف CSV بترميز UTF-8 بالأعمدة: kind, passage, book, author, chapter, hadith_number, volume, page, edition, url, note. صف واحد لكل نص كامل. الحد الأقصى ٢ ميجابايت / ٣٠٠٠ صف.',
    importFile: 'استيراد الملف', statsTitle: 'إحصاءات الفهارس', loadingStats: 'جارٍ التحميل…',
    addTitle: 'إضافة مصدر',
    addSubtitle: 'أضف نصًا تحققت منه مقابل طبعة فعلية. لا يتحقق النموذج من صحة المدخلات آليًا.',
    passageRequired: 'نص النقل أو الحديث *', bookRequired: 'عنوان الكتاب *', authorRequired: 'المؤلف *',
    volume: 'المجلد', page: 'الصفحة', referenceRequired: 'بيانات الطبعة / المرجع *',
    sourceUrlOptional: 'رابط المصدر (اختياري)', sourceUrl: 'رابط المصدر', notes: 'ملاحظات',
    verifyText: 'راجعتُ هذا النص وبياناته الببليوغرافية مقابل الطبعة المذكورة.',
    addToLocal: 'إضافة إلى الفهرس المحلي', adminTitle: 'الإدارة',
    adminSubtitle: 'يمكن للمدير فقط إضافة السجلات أو استيرادها أو حذفها. يستطيع الطلاب البحث ونسخ الاستشهادات دون تسجيل دخول.',
    signedInAs: 'الحساب الحالي', signOut: 'تسجيل الخروج', accountsList: 'الحسابات المسجلة',
    adminTools: 'أدوات المدير', addVerifiedHadith: 'إضافة حديث موثّق',
    hadithTextRequired: 'نص الحديث كاملًا *', chapter: 'الباب', hadithNumber: 'رقم الحديث',
    verifyRecord: 'راجعتُ هذا السجل مقابل المصدر المذكور.', addHadith: 'إضافة الحديث',
    manageRecords: 'إدارة السجلات المحلية', loadRecords: 'تحميل السجلات',
    ethicsTitle: 'أمانة البحث:',
    ethicsText: 'يبحث هذا النموذج في المكتبة الشاملة عبر وصلتها الرسمية للقراءة فقط، وفي الدرر السنية عبر خدمة البحث العامة، ويحتفظ بفهارسك المحلية منفصلة. لا يتحقق من صحة الأحاديث أو أسانيدها أو درجاتها عند العلماء. راجع الصفحة الأصلية قبل الاقتباس، ولا تُعرض أرقام الصفحات إلا إذا كانت محفوظة لطبعة محددة.',
    footerLine: 'الاسترجاع الدلالي ونظام الاستشهاد لنصوص أحاديث الأحكام',
    footerNote: 'استرجاع فقط — لا أحكام مولّدة آليًا',
    authTitle: 'الحساب', close: 'إغلاق', authHint: 'أول حساب يُنشأ يصبح حساب المدير.',
    username: 'اسم المستخدم', password: 'كلمة المرور', createAdmin: 'إنشاء حساب المدير',
    needAccount: 'ليس لديك حساب؟ إنشاء حساب', createUser: 'إنشاء حساب مستخدم',
    haveAccount: 'لديك حساب؟ تسجيل الدخول', adminPanel: 'لوحة الإدارة',
    admin: 'مدير', user: 'مستخدم', local: 'محلي', google: 'Google',
    usernameOrEmail: 'اسم المستخدم أو البريد الإلكتروني', email: 'البريد الإلكتروني',
    role: 'الدور', provider: 'طريقة الدخول', created: 'تاريخ الإنشاء',
    usersTitle: 'المستخدمون', usersSubtitle: 'قائمة الحسابات المسجلة مع اسم المستخدم والبريد الإلكتروني الفريد وطريقة الدخول.',
    historyTitle: 'سجل البحث', historySubtitle: 'تظهر هنا عمليات البحث التي أجريتها بعد تسجيل الدخول. عمليات الضيوف لا تُحفظ.',
    mySearches: 'عمليات البحث الخاصة بي', clearHistory: 'مسح السجل',
    noHistory: 'لا توجد عمليات بحث محفوظة بعد.', historyCleared: 'تم مسح سجل البحث.',
    googleSignIn: 'المتابعة باستخدام Gmail',
    googleNote: 'دخول Gmail غير مُعدّ على هذا الخادم.',
    googleFailed: 'تعذّر تسجيل الدخول بـ Gmail. حاول مرة أخرى.',
    googleStateFailed: 'انتهت صلاحية طلب دخول Gmail. حاول مرة أخرى.',
    googleUnverified: 'لم يتم تأكيد بريد Gmail. استخدم بريدًا موثّقًا.',
    emailTaken: 'هذا البريد الإلكتروني مستخدم بالفعل.',
    invalidEmail: 'أدخل بريدًا إلكترونيًا صالحًا.',
    signInRequired: 'يتطلب تسجيل الدخول.',
    searchingShamela: 'جارٍ البحث في المكتبة الشاملة…',
    searchingDorar: 'جارٍ البحث في الدرر السنية…',
    searchingLocal: 'جارٍ البحث في الفهارس المحلية…', searching: 'جارٍ البحث…',
    found: 'تم العثور على {count} نتيجة', fromShamela: 'من المكتبة الشاملة',
    fromDorar: 'من الدرر السنية',
    retrieved: 'نتائج مسترجعة', reviewBeforeQuote: 'راجع المصدر قبل الاقتباس',
    noShamela: 'لا توجد مطابقة في المكتبة الشاملة لهذا النص. جرّب عبارة أقصر.',
    noDorar: 'لا توجد مطابقة في الدرر السنية لهذا النص. جرّب عبارة أقصر.',
    dorarUnavailable: 'تعذّر الاتصال بالدرر السنية. حاول مرة أخرى.',
    dorarRateLimit: 'تجاوزت حد الطلبات في الدرر السنية. حاول لاحقًا.',
    dorarBadResponse: 'استجابة غير مفهومة من الدرر السنية.',
    noLocal: 'لا توجد مطابقة في الفهرس المحلي. هذا لا يعني أن المصدر غير موجود.',
    unknownSource: 'مصدر غير محدد', pageShort: 'صفحة', referenceMissing: 'المرجع غير محدد',
    shamelaMatch: 'مطابقة من المكتبة الشاملة', dorarMatch: 'مطابقة من الدرر السنية',
    textMatch: 'مطابقة نصية', possibleMatch: 'مطابقة محتملة',
    shamelaProvenance: 'مقتطف من المكتبة الشاملة — راجع الصفحة قبل الاقتباس',
    dorarProvenance: 'مقتطف من الدرر السنية — راجع الصفحة قبل الاقتباس',
    citationLabel: 'الاستشهاد المقترح', copyCitation: 'نسخ الاستشهاد',
    sourceOriginal: 'المصدر الأصلي ↗', copied: 'تم نسخ الاستشهاد',
    copyFailed: 'تعذّر النسخ — حدد النص وانسخه يدويًا',
    statsImport: '{name}: {count} مقطع {kind}', noImports: 'لا توجد مقاطع مستوردة بعد.',
    statsFail: 'تعذّر تحميل إحصاءات الفهارس.', chooseCsv: 'اختر ملف CSV أولًا.',
    searchImported: 'جارٍ البحث في المقاطع المستوردة…', noBookMatches: 'لا توجد مطابقة بين المقاطع المستوردة.',
    searchFailed: 'فشل البحث', addFailed: 'فشل الإضافة', loadFailed: 'تعذّر التحميل',
    adminSignedIn: 'مدير النظام مسجّل الدخول.', signInToManage: 'سجّل الدخول لإدارة المصادر.',
    createAdminPrompt: 'أنشئ أول حساب ليصبح حساب المدير.',
    signedInAsUser: 'مسجّل الدخول: {name} ({role})', deleteConfirm: 'حذف هذا السجل نهائيًا؟',
    noRecords: 'لا توجد سجلات بعد.', accountCreated: 'تم إنشاء الحساب.',
    adminCreated: 'تم إنشاء حساب المدير.', loggedIn: 'تم تسجيل الدخول.',
    loggedOut: 'تم تسجيل الخروج.', wrongCredentials: 'اسم المستخدم أو كلمة المرور غير صحيحة.',
    usernameTaken: 'اسم المستخدم مستخدم بالفعل.', invalidUsername: 'اسم المستخدم يجب أن يكون ٣ إلى ٣٢ حرفًا أو رقمًا أو نقطة أو شرطة.',
    invalidPassword8: 'كلمة المرور يجب أن تكون ٨ إلى ٢٥٦ حرفًا.',
    invalidPassword12: 'كلمة المرور يجب أن تكون ١٢ إلى ٢٥٦ حرفًا.',
    adminExists: 'حساب المدير مُنشأ بالفعل.', adminRequired: 'يتطلب تسجيل دخول المدير.',
    notFound: 'غير موجود.', crossOrigin: 'تم رفض الطلب من مصدر مختلف.',
    invalidSize: 'حجم الطلب غير صالح.', genericError: 'حدث خطأ غير متوقع.',
    invalidQuery: 'أدخل ٣ إلى ٢٠٠٠ حرف.', invalidCategory: 'فئة بحث غير صالحة.',
    requiredFields: 'النص والكتاب والمؤلف والمرجع مطلوبة.',
    fieldTooLong: 'أحد الحقول طويل جدًا.', invalidUrl: 'رابط غير صالح.',
    confirmVerification: 'أكّد أنك راجعت النص مقابل الطبعة المذكورة.',
    invalidCsv: 'ملف CSV غير صالح.', fileTooLarge: 'حجم الملف يتجاوز ٢ ميجابايت.',
    maxRecords: 'الحد الأقصى ٣٠٠٠ سجل لكل استيراد.',
    invalidRow: 'كل صف يحتاج إلى نوع ونص وكتاب ومؤلف.',
    invalidRecordId: 'معرّف السجل غير صالح.', adminAuthRequired: 'يتطلب صلاحيات المدير.'
  },
  en: {
    pageTitle: 'Hadith Research Assistant — Search & Citation',
    brandTitle: 'Hadith Research Guide',
    brandSubtitle: 'Retrieval and citation for hadith and classical quotations',
    mainNav: 'Main navigation', navAsk: 'Ask', navWorkspace: 'Workspace',
    navHistory: 'History', navUsers: 'Users', navSources: 'Sources', navAdmin: 'Admin',
    themeToggle: 'Toggle theme', openMenu: 'Open menu', signIn: 'Sign in',
    chatTitle: 'Hadith and quotation research assistant',
    chatSubtitle: 'Retrieve texts and their sources from Shamela, Dorar.net, or your local catalog — no legal rulings generated.',
    queryLabel: 'Type a hadith or quotation to search',
    queryPlaceholder: 'Type the text here… (Enter to search)',
    scopeLabel: 'Search scope', scopeShamela: 'Shamela library',
    scopeDorar: 'Dorar.net (الدرر السنية)',
    scopeHadith: 'Hadith (local catalog)', scopeQuote: 'Quotations (local catalog)',
    scopeAll: 'All sources (local)',
    methodNote: 'Results are limited to four books: Sahih al-Bukhari, Sahih Muslim, Sunan Abi Dawud, and Jami\' at-Tirmidhi — retrieval only, no fatwas.',
    methodNoteDorar: 'Dorar.net shows the text, source, and the scholar\'s grade summary — retrieval only, no fatwas.',
    methodNoteLocal: 'Searching only the catalogs you imported — retrieval only, no fatwas.',
    send: 'Search', emptyTitle: 'Every text with its source.',
    emptyHint: 'Type part of a hadith or quotation. Matching texts appear from Shamela, Dorar.net, or your catalogs with a source link.',
    booksTitle: 'Workspace',
    booksSubtitle: 'Search imported excerpts from your books and manage your local catalogs.',
    bookSearchTitle: 'Search my imported books',
    bookSearchHint: 'This catalog searches quotations you import yourself. No complete library or Shamela copy is bundled, and imported records are not verified automatically.',
    textKind: 'Text type', wordHadith: 'Hadith', wordQuote: 'Classical quotation',
    textOrExcerpt: 'Text or excerpt', bookQueryPlaceholder: 'Enter part of a hadith or text',
    searchMyBooks: 'Search my books', importTitle: 'Import a book catalog', adminOnly: 'Admin only',
    importHint: 'Upload a UTF-8 CSV with columns: kind, passage, book, author, chapter, hadith_number, volume, page, edition, url, note. One complete text per row. Maximum 2 MB / 3000 rows.',
    importFile: 'Import file', statsTitle: 'Catalog statistics', loadingStats: 'Loading…',
    addTitle: 'Add a source',
    addSubtitle: 'Add a text you checked against a real edition. The app does not verify entries automatically.',
    passageRequired: 'Hadith or quotation text *', bookRequired: 'Book title *', authorRequired: 'Author *',
    volume: 'Volume', page: 'Page', referenceRequired: 'Edition / reference *',
    sourceUrlOptional: 'Source URL (optional)', sourceUrl: 'Source URL', notes: 'Notes',
    verifyText: 'I checked this text and its bibliographic details against the stated edition.',
    addToLocal: 'Add to local catalog', adminTitle: 'Administration',
    adminSubtitle: 'Only an admin can add, import, or delete records. Students can search and copy citations without signing in.',
    signedInAs: 'Current account', signOut: 'Sign out', accountsList: 'Registered accounts',
    adminTools: 'Admin tools', addVerifiedHadith: 'Add a verified hadith',
    hadithTextRequired: 'Complete hadith text *', chapter: 'Chapter', hadithNumber: 'Hadith number',
    verifyRecord: 'I checked this record against the stated source.', addHadith: 'Add hadith',
    manageRecords: 'Manage local records', loadRecords: 'Load records',
    ethicsTitle: 'Research integrity:',
    ethicsText: 'This app searches Shamela through its official read-only connector and Dorar.net through its public search service, while keeping your local catalogs separate. It does not verify authenticity, chains of narrators, or scholarly grades. Check the original page before citing, and only show page numbers preserved for a specific edition.',
    footerLine: 'Semantic retrieval and citation system for hadith texts',
    footerNote: 'Retrieval only — no generated rulings',
    authTitle: 'Account', close: 'Close', authHint: 'The first account created becomes the administrator.',
    username: 'Username', password: 'Password', createAdmin: 'Create admin account',
    needAccount: 'No account? Create one', createUser: 'Create user account',
    haveAccount: 'Have an account? Sign in', adminPanel: 'Admin panel',
    admin: 'Admin', user: 'User', local: 'Local', google: 'Google',
    usernameOrEmail: 'Username or email', email: 'Email',
    role: 'Role', provider: 'Sign-in method', created: 'Created',
    usersTitle: 'Users', usersSubtitle: 'Registered accounts with username, unique email, and sign-in method.',
    historyTitle: 'Search history', historySubtitle: 'Searches you made while signed in appear here. Guest searches are not saved.',
    mySearches: 'My searches', clearHistory: 'Clear history',
    noHistory: 'No saved searches yet.', historyCleared: 'Search history cleared.',
    googleSignIn: 'Continue with Gmail',
    googleNote: 'Gmail sign-in is not configured on this server.',
    googleFailed: 'Could not sign in with Gmail. Please try again.',
    googleStateFailed: 'The Gmail sign-in request expired. Please try again.',
    googleUnverified: 'Your Gmail address is not verified. Use a verified account.',
    emailTaken: 'This email is already registered.',
    invalidEmail: 'Enter a valid email address.',
    signInRequired: 'Sign-in required.',
    searchingShamela: 'Searching Shamela library…',
    searchingDorar: 'Searching Dorar.net…',
    searchingLocal: 'Searching local catalogs…', searching: 'Searching…',
    found: '{count} results found', fromShamela: 'From Shamela',
    fromDorar: 'From Dorar.net',
    retrieved: 'Retrieved results', reviewBeforeQuote: 'Check the source before citing',
    noShamela: 'No match found in Shamela for this text. Try a shorter phrase.',
    noDorar: 'No match found in Dorar.net for this text. Try a shorter phrase.',
    dorarUnavailable: 'Dorar.net is unavailable right now. Please try again.',
    dorarRateLimit: 'Too many requests to Dorar.net. Please try again later.',
    dorarBadResponse: 'Could not read the response from Dorar.net.',
    noLocal: 'No match in the local catalog. This does not mean the source does not exist.',
    unknownSource: 'Source not specified', pageShort: 'Page', referenceMissing: 'Reference not specified',
    shamelaMatch: 'Shamela match', dorarMatch: 'Dorar.net match',
    textMatch: 'Text match', possibleMatch: 'Possible match',
    shamelaProvenance: 'Excerpt from Shamela — check the page before citing',
    dorarProvenance: 'Excerpt from Dorar.net — check the page before citing',
    citationLabel: 'Suggested citation', copyCitation: 'Copy citation',
    sourceOriginal: 'Original source ↗', copied: 'Citation copied',
    copyFailed: 'Copy failed — select the text and copy it manually',
    statsImport: '{name}: {count} {kind} excerpt(s)', noImports: 'No imported excerpts yet.',
    statsFail: 'Could not load catalog statistics.', chooseCsv: 'Choose a CSV file first.',
    searchImported: 'Searching imported excerpts…', noBookMatches: 'No match in imported excerpts.',
    searchFailed: 'Search failed', addFailed: 'Could not add', loadFailed: 'Could not load',
    adminSignedIn: 'Administrator signed in.', signInToManage: 'Sign in to manage sources.',
    createAdminPrompt: 'Create the first account to become the administrator.',
    signedInAsUser: 'Signed in as {name} ({role})', deleteConfirm: 'Delete this record permanently?',
    noRecords: 'No records yet.', accountCreated: 'Account created.',
    adminCreated: 'Administrator account created.', loggedIn: 'Signed in.',
    loggedOut: 'Signed out.', wrongCredentials: 'Incorrect username or password.',
    usernameTaken: 'Username already exists.', invalidUsername: 'Username must be 3-32 letters, numbers, dots, dashes, or underscores.',
    invalidPassword8: 'Password must contain 8-256 characters.',
    invalidPassword12: 'Password must contain 12-256 characters.',
    adminExists: 'Admin account already configured.', adminRequired: 'Admin sign-in required.',
    notFound: 'Not found.', crossOrigin: 'Cross-origin request denied.',
    invalidSize: 'Invalid request size.', genericError: 'Unexpected server error.',
    invalidQuery: 'Enter 3-2000 characters.', invalidCategory: 'Invalid search category.',
    requiredFields: 'Text, book, author, and reference are required.',
    fieldTooLong: 'A field is too long.', invalidUrl: 'Invalid source URL.',
    confirmVerification: 'Confirm that you checked the text against the stated source.',
    invalidCsv: 'Invalid CSV file.', fileTooLarge: 'File is larger than 2 MB.',
    maxRecords: 'Maximum 3000 records per import.',
    invalidRow: 'Each row needs a type, text, book, and author.',
    invalidRecordId: 'Invalid record ID.', adminAuthRequired: 'Administrator authentication required.'
  }
};

let lang = 'ar';
try { lang = localStorage.getItem('ra-lang') === 'en' ? 'en' : 'ar'; } catch (error) { /* storage blocked */ }

const $ = (id) => document.getElementById(id);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) {
    if (text instanceof Node) node.append(text);
    else node.textContent = text;
  }
  return node;
}

function t(key, vars = {}, fallback = key) {
  let value = (I18N[lang] && I18N[lang][key]) || fallback;
  Object.entries(vars).forEach(([name, replacement]) => {
    value = value.replace(new RegExp('\\{' + name + '\\}', 'g'), String(replacement));
  });
  return value;
}

const ERROR_KEYS = {
  'username is required': 'invalidUsername',
  'username must be 3-32 letters, numbers, dots, dashes, or underscores': 'invalidUsername',
  'password must contain 8-256 characters': 'invalidPassword8',
  'password must contain 12-256 characters': 'invalidPassword12',
  'admin password must contain 12-256 characters': 'invalidPassword12',
  'username already exists': 'usernameTaken',
  'email already registered': 'emailTaken',
  'email is required': 'invalidEmail',
  'invalid email address': 'invalidEmail',
  'username or email is required': 'invalidUsername',
  'sign-in required': 'signInRequired',
  'admin account already configured': 'adminExists',
  'admin already configured': 'adminExists',
  'incorrect username or password': 'wrongCredentials',
  'admin login required': 'adminRequired',
  'administrator authentication required': 'adminAuthRequired',
  'not found': 'notFound',
  'record not found': 'notFound',
  'cross-origin request denied': 'crossOrigin',
  'invalid request size': 'invalidSize',
  'enter 3-2000 characters': 'invalidQuery',
  'text must be a string': 'invalidQuery',
  'invalid search category': 'invalidCategory',
  'passage, book, author, and reference are required': 'requiredFields',
  'hadith text, book, author, and reference are required': 'requiredFields',
  'field too long': 'fieldTooLong',
  'url must start with https:// or http://': 'invalidUrl',
  'invalid source url': 'invalidUrl',
  'confirm that you checked the quotation against the named edition': 'confirmVerification',
  'confirm that you checked the hadith against the source': 'confirmVerification',
  'invalid filename': 'invalidCsv',
  'csv needs kind,passage,book,author columns': 'invalidCsv',
  'use csv for book imports so each passage has traceable source metadata': 'invalidCsv',
  'only utf-8 csv files are supported': 'invalidCsv',
  'file too large (2 mb limit)': 'fileTooLarge',
  'maximum 3000 records per import': 'maxRecords',
  'no records found': 'noRecords',
  'every row needs kind (hadith/quote), passage, book, author': 'invalidRow',
  'invalid record id': 'invalidRecordId',
  'تعذّر الاتصال بموقع الدرر السنية': 'dorarUnavailable',
  'تعذّر الوصول إلى موقع الدرر السنية': 'dorarUnavailable',
  'تجاوزت حد الطلبات في موقع الدرر السنية. حاول لاحقًا': 'dorarRateLimit',
  'استجابة غير مفهومة من الدرر السنية': 'dorarBadResponse',
  'اكتب نصًا للبحث أولًا': 'invalidQuery',
  'unexpected server error': 'genericError'
};

function errorText(error) {
  const raw = error && error.message ? String(error.message) : t('genericError');
  const normalized = raw.trim().toLowerCase().replace(/[–—]/g, '-').replace(/\.$/, '');
  const key = ERROR_KEYS[normalized];
  return key ? t(key) : raw;
}

let authStatus = { user: null, admin: false, needsSetup: true, googleEnabled: false };
let statusTimer;
let toastTimer;

/* ------------------------------------------------------------
   Language and theme
   ------------------------------------------------------------ */
function syncMethodNote() {
  const note = $('method-note');
  if (!note) return;
  const key = $('scope').value === 'shamela' ? 'methodNote'
    : $('scope').value === 'dorar' ? 'methodNoteDorar' : 'methodNoteLocal';
  note.dataset.i18n = key;
  note.textContent = t(key);
}

function applyLanguage(next) {
  lang = next === 'en' ? 'en' : 'ar';
  try { localStorage.setItem('ra-lang', lang); } catch (error) { /* storage blocked */ }
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'en' ? 'ltr' : 'rtl';
  document.title = t('pageTitle');

  $$('[data-i18n]').forEach((node) => {
    const value = I18N[lang][node.dataset.i18n];
    if (value !== undefined) node.textContent = value;
  });
  $$('[data-i18n-placeholder]').forEach((node) => {
    const value = I18N[lang][node.dataset.i18nPlaceholder];
    if (value !== undefined) node.placeholder = value;
  });
  $$('[data-i18n-title]').forEach((node) => {
    const value = I18N[lang][node.dataset.i18nTitle];
    if (value !== undefined) {
      node.title = value;
      node.setAttribute('aria-label', value);
    }
  });

  $('lang-label').textContent = lang === 'ar' ? 'EN' : 'ع';
  $('lang-toggle').title = lang === 'ar' ? 'English' : 'العربية';
  $('lang-toggle').setAttribute('aria-label', lang === 'ar' ? 'English' : 'العربية');
  syncThemeLabel();
  updateAuthUI(authStatus);
  updateAdminUI(authStatus);
  syncMethodNote();
}

const themeToggle = $('theme-toggle');
function syncThemeLabel() {
  const dark = document.documentElement.classList.contains('dark');
  const label = t('themeToggle');
  themeToggle.setAttribute('aria-label', label);
  themeToggle.title = dark ? t('themeToggle') : t('themeToggle');
}
syncThemeLabel();
themeToggle.addEventListener('click', () => {
  const dark = document.documentElement.classList.toggle('dark');
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  try { localStorage.setItem('ra-theme', dark ? 'dark' : 'light'); } catch (error) { /* storage blocked */ }
  syncThemeLabel();
});
document.documentElement.classList.add('theme-ready');
$('lang-toggle').addEventListener('click', () => applyLanguage(lang === 'ar' ? 'en' : 'ar'));

/* ------------------------------------------------------------
   Navigation and helpers
   ------------------------------------------------------------ */
function setView(view) {
  $$('.view').forEach((section) => { section.hidden = section.id !== view + '-view'; });
  $$('.nav-link').forEach((button) => button.classList.toggle('active', button.dataset.view === view));
  closeNavDrawer();
  if (view === 'books') showBookStats();
  if (view === 'users' && authStatus.admin) loadUsersTable();
  if (view === 'history' && authStatus.user) loadHistory();
  if (view === 'admin' && authStatus.admin) loadUsers();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

$$('[data-view]').forEach((button) => {
  button.addEventListener('click', (event) => { event.preventDefault(); setView(button.dataset.view); });
});
$('brand-home').addEventListener('click', (event) => { event.preventDefault(); setView('ask'); });
const navDrawer = $('nav-drawer');
const navBackdrop = $('nav-backdrop');
navDrawer.inert = true;

function openNavDrawer() {
  navDrawer.inert = false;
  navDrawer.classList.add('is-open');
  navBackdrop.classList.add('is-open');
  navDrawer.setAttribute('aria-hidden', 'false');
  $('menu-btn').setAttribute('aria-expanded', 'true');
  document.body.classList.add('nav-open');
}
function closeNavDrawer() {
  navDrawer.inert = true;
  navDrawer.classList.remove('is-open');
  navBackdrop.classList.remove('is-open');
  navDrawer.setAttribute('aria-hidden', 'true');
  $('menu-btn').setAttribute('aria-expanded', 'false');
  document.body.classList.remove('nav-open');
}
$('menu-btn').addEventListener('click', () => {
  if (navDrawer.classList.contains('is-open')) closeNavDrawer();
  else openNavDrawer();
});
$('drawer-close').addEventListener('click', closeNavDrawer);
navBackdrop.addEventListener('click', closeNavDrawer);
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && navDrawer.classList.contains('is-open')) closeNavDrawer();
});

const composerWrap = $('composer-wrap');
function syncComposerDock() {
  const docked = window.scrollY > 24;
  if (docked && !composerWrap.classList.contains('is-docked')) {
    document.documentElement.style.setProperty('--composer-h', `${$('ask-form').offsetHeight}px`);
  }
  composerWrap.classList.toggle('is-docked', docked);
  document.body.classList.toggle('composer-docked', docked);
}
window.addEventListener('scroll', syncComposerDock, { passive: true });
syncComposerDock();

function setStatus(text) {
  const target = $('status');
  target.textContent = text || '';
  clearTimeout(statusTimer);
  if (text) statusTimer = setTimeout(() => { target.textContent = ''; }, 4500);
}

function showToast(text) {
  const toast = $('toast');
  toast.textContent = text;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 1800);
}

async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const helper = el('textarea', 'sr-only', text);
      document.body.append(helper);
      helper.select();
      document.execCommand('copy');
      helper.remove();
    }
    showToast(t('copied'));
  } catch (error) {
    showToast(t('copyFailed'));
  }
}

async function postJSON(path, payload) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || t('genericError'));
  return body;
}

/* ------------------------------------------------------------
   Shared result card
   ------------------------------------------------------------ */
const MATCH_KEYS = {
  'مطابقة من المكتبة الشاملة': 'shamelaMatch',
  'مطابقة من الدرر السنية': 'dorarMatch',
  'مطابقة نصية': 'textMatch',
  'مطابقة محتملة': 'possibleMatch'
};
const PROVENANCE_KEYS = {
  'مقتطف من المكتبة الشاملة — راجع الصفحة قبل الاقتباس': 'shamelaProvenance',
  'مقتطف من الدرر السنية — راجع الصفحة قبل الاقتباس': 'dorarProvenance'
};

function translateRecordText(value) {
  return t(PROVENANCE_KEYS[value] || '__none__', {}, value);
}

function buildResultCard(record, index, options = {}) {
  const card = el('article', 'result glass');
  const top = el('div', 'result-top');
  const matchKey = MATCH_KEYS[record.match_label];
  top.append(el('span', 'pill', matchKey ? t(matchKey) : (record.match_label || t('textMatch'))));
  if (index) top.append(el('span', 'result-index', `#${index}`));
  card.append(top, el('h3', 'result-title', record.book || t('unknownSource')));
  card.append(el('p', 'arabic', record.passage || ''));

  if (record.provenance) card.append(el('p', 'meta', translateRecordText(record.provenance)));
  const sourceDetail = record.kind === 'shamela'
    ? `${t('pageShort')} ${record.page_id}`
    : (record.chapter || record.reference || t('referenceMissing'));
  const details = [record.author, sourceDetail].filter(Boolean).join(' · ');
  card.append(el('p', 'meta', details));
  if (options.imported) card.append(el('p', 'meta', `${record.import_name || t('unknownSource')} · ${t('retrieved')}`));
  if (record.note) card.append(el('p', 'meta', record.note));

  const citation = el('div', 'citation');
  citation.append(el('span', 'citation-label', t('citationLabel')));
  citation.append(el('p', '', record.citation_text || record.footnote || ''));
  card.append(citation);

  const actions = el('div', 'result-actions');
  const copy = el('button', 'copy-btn', t('copyCitation'));
  copy.type = 'button';
  copy.addEventListener('click', () => copyText(record.footnote || ''));
  actions.append(copy);

  if (record.url) {
    const link = el('a', 'source-link', t('sourceOriginal'));
    link.href = record.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    actions.append(link);
  }
  card.append(actions);
  return card;
}

/* ------------------------------------------------------------
   Ask / search
   ------------------------------------------------------------ */
const queryInput = $('query');
const sendButton = $('search');

$('scope').addEventListener('change', syncMethodNote);

function syncSendButton() { sendButton.disabled = !queryInput.value.trim(); }
function resizeInput() {
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 200) + 'px';
}
queryInput.addEventListener('input', () => { syncSendButton(); resizeInput(); });
queryInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    $('ask-form').requestSubmit();
  }
});
syncSendButton();

function revealConversation() {
  const conversation = $('conversation');
  const offset = Math.min(230, Math.max(150, window.innerHeight * 0.3));
  const top = conversation.getBoundingClientRect().top + window.scrollY - offset;
  window.scrollTo({ top: Math.max(top, 0), behavior: 'smooth' });
}

function recordHistory(query, scope, resultCount) {
  if (!authStatus.user) return;
  postJSON('/api/history', {
    query, scope, result_count: resultCount
  }).catch(() => { /* history is best-effort */ });
}

async function runSearch(query, scope) {
  $('empty-state').hidden = true;
  $('chat-shell').classList.add('has-results');
  const conversation = $('conversation');
  const fromShamela = scope === 'shamela';
  const fromDorar = scope === 'dorar';
  const loadingKey = fromShamela ? 'searchingShamela' : fromDorar ? 'searchingDorar' : 'searchingLocal';
  const badgeKey = fromShamela ? 'fromShamela' : fromDorar ? 'fromDorar' : 'retrieved';
  const emptyKey = fromShamela ? 'noShamela' : fromDorar ? 'noDorar' : 'noLocal';

  const bubble = el('div', 'user-bubble', query);
  bubble.dir = 'auto';
  conversation.append(bubble);

  const answer = el('div', 'answer');
  answer.append(el('div', 'answer-loading', t(loadingKey)));
  conversation.append(answer);
  revealConversation();

  setStatus(t('searching'));
  try {
    let results;
    if (fromShamela) {
      const data = await postJSON('/api/shamela/search', { query, kind: 'all' });
      results = data.results || [];
    } else if (fromDorar) {
      const data = await postJSON('/api/dorar/search', { query });
      results = data.results || [];
    } else {
      const kinds = scope === 'all' ? ['hadith', 'quote'] : [scope];
      const batches = await Promise.all(kinds.map((kind) =>
        postJSON('/api/search/all', { kind, query }).then((data) => data.results || [])
      ));
      results = batches.flat();
    }

    const head = el('div', 'answer-head');
    head.append(el('span', 'answer-badge', t(badgeKey)));
    head.append(el('span', 'answer-count', `${t('found', { count: results.length })} · ${t('reviewBeforeQuote')}`));
    answer.replaceChildren(head);

    if (!results.length) {
      answer.append(el('p', 'muted', t(emptyKey)));
    } else {
      results.forEach((record, position) => answer.append(buildResultCard(record, position + 1)));
    }
    setStatus(t('found', { count: results.length }));
    recordHistory(query, scope, results.length);
  } catch (error) {
    answer.replaceChildren(el('p', 'error', errorText(error)));
    setStatus('');
    recordHistory(query, scope, 0);
  }
  revealConversation();
}

$('ask-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;
  runSearch(query, $('scope').value);
  queryInput.value = '';
  syncSendButton();
  resizeInput();
  queryInput.focus();
});

$$('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    queryInput.value = chip.dataset.q;
    $('scope').value = 'shamela';
    syncSendButton();
    $('ask-form').requestSubmit();
  });
});

/* ------------------------------------------------------------
   Imported books workspace
   ------------------------------------------------------------ */
async function showBookStats() {
  try {
    const response = await fetch('/api/books/stats');
    const data = await response.json();
    const imports = data.imports || [];
    $('book-stats').textContent = imports.length
      ? imports.map((item) => t('statsImport', {
          name: item.import_name,
          count: item.count,
          kind: t(item.kind === 'hadith' ? 'wordHadith' : 'wordQuote')
        })).join(' · ')
      : t('noImports');
  } catch (error) {
    $('book-stats').textContent = t('statsFail');
  }
}

$('book-import').addEventListener('click', async () => {
  const file = $('book-file').files[0];
  if (!file) { $('import-status').textContent = t('chooseCsv'); return; }
  try {
    const content = await file.text();
    const data = await postJSON('/api/books/import', { filename: file.name, content });
    $('import-status').textContent = data.message || t('importFile');
    showBookStats();
  } catch (error) {
    $('import-status').textContent = errorText(error);
  }
});

$('book-search').addEventListener('click', async () => {
  const container = $('books-results');
  container.replaceChildren();
  $('book-status').textContent = t('searchImported');
  try {
    const data = await postJSON('/api/books/search', {
      kind: $('book-kind').value, query: $('book-query').value
    });
    $('book-status').textContent = t('found', { count: data.results.length });
    if (!data.results.length) container.append(el('p', 'muted', t('noBookMatches')));
    data.results.forEach((record, position) => container.append(buildResultCard(record, position + 1, { imported: true })));
  } catch (error) {
    $('book-status').textContent = errorText(error) || t('searchFailed');
  }
});

/* ------------------------------------------------------------
   Add a quotation (admin only on the server)
   ------------------------------------------------------------ */
$('add-panel').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form));
  payload.verified = payload.verified === 'true';
  try {
    const data = await postJSON('/api/quotes', payload);
    $('add-status').textContent = data.message || t('addToLocal');
    form.reset();
  } catch (error) {
    $('add-status').textContent = errorText(error) || t('addFailed');
  }
});

/* ------------------------------------------------------------
   Accounts and admin controls
   ------------------------------------------------------------ */
const authDialog = $('auth-dialog');

function showAuthForm(which) {
  $('auth-setup').hidden = which !== 'setup';
  $('auth-login').hidden = which !== 'login';
  $('auth-register').hidden = which !== 'register';
  $('auth-signed-actions').hidden = !authStatus.user;
  $('auth-error').textContent = '';
}

function updateAuthUI(status) {
  const user = status.user;
  $('account-name').textContent = user ? user.username : t('signIn');
  const badge = $('account-role');
  badge.hidden = !user;
  badge.textContent = user ? t(user.admin ? 'admin' : 'user') : '';
  badge.classList.toggle('admin', Boolean(user && user.admin));

  if (status.needsSetup) showAuthForm('setup');
  else if (user) { showAuthForm('none'); }
  else if (!$('auth-register').hidden) showAuthForm('register');
  else showAuthForm('login');

  $('auth-hint').textContent = t('authHint');
  $('auth-logout').hidden = !user;
  $('auth-admin-link').hidden = !(user && user.admin);
  $$('.user-only').forEach((node) => { node.hidden = !user; });
  $$('.admin-only').forEach((node) => { node.hidden = !(user && user.admin); });

  const googleAvailable = Boolean(status.googleEnabled && !status.needsSetup);
  $('google-signin').hidden = !googleAvailable;
  const note = $('google-note');
  note.hidden = googleAvailable;
  note.textContent = status.googleEnabled ? t('createAdminPrompt') : t('googleNote');
}

function updateAdminUI(status) {
  const user = status.user;
  const admin = Boolean(user && user.admin);
  $('admin-tools').hidden = !admin;
  $('admin-import').hidden = !admin;
  $('admin-users-card').hidden = !admin;
  $('admin-status').textContent = user
    ? t('signedInAsUser', { name: user.username, role: t(user.admin ? 'admin' : 'user') })
    : t(status.needsSetup ? 'createAdminPrompt' : 'signInToManage');
}

async function refreshAuth() {
  try {
    const response = await fetch('/api/auth/status');
    authStatus = await response.json();
    updateAuthUI(authStatus);
    updateAdminUI(authStatus);
    if (authStatus.admin) loadUsers();
  } catch (error) {
    authStatus = { user: null, admin: false, needsSetup: false, googleEnabled: false };
    updateAuthUI(authStatus);
    updateAdminUI(authStatus);
  }
}

async function submitAuth(path, payload, messageKey) {
  try {
    const data = await postJSON(path, payload);
    authDialog.close();
    showToast(t(messageKey));
    await refreshAuth();
    return data;
  } catch (error) {
    $('auth-error').textContent = errorText(error);
    return null;
  }
}

$('login-btn').addEventListener('click', () => {
  $('auth-error').textContent = '';
  updateAuthUI(authStatus);
  if (!authDialog.open) authDialog.showModal();
});
$('auth-close').addEventListener('click', () => authDialog.close());
$('show-register').addEventListener('click', () => showAuthForm('register'));
$('show-login').addEventListener('click', () => showAuthForm('login'));

$('google-signin').addEventListener('click', async () => {
  $('auth-error').textContent = '';
  try {
    const response = await fetch('/api/auth/google/start');
    const data = await response.json();
    if (!response.ok || !data.url) throw new Error(data.error || t('googleFailed'));
    window.location.href = data.url;
  } catch (error) {
    $('auth-error').textContent = errorText(error);
  }
});

function handleAuthRedirect() {
  const params = new URLSearchParams(window.location.search);
  const authError = params.get('auth_error');
  if (authError) {
    const key = authError === 'google_state' ? 'googleStateFailed'
      : authError === 'google_unverified' ? 'googleUnverified' : 'googleFailed';
    showToast(t(key));
  } else if (params.get('google') === 'ok') {
    showToast(t('loggedIn'));
  }
  if (authError || params.has('google')) {
    history.replaceState({}, '', window.location.pathname);
  }
}

$('auth-setup').addEventListener('submit', (event) => {
  event.preventDefault();
  const payload = {
    username: $('setup-username').value.trim(),
    email: $('setup-email').value.trim(),
    password: $('setup-password').value
  };
  submitAuth('/api/auth/setup', payload, 'adminCreated');
});

$('auth-register').addEventListener('submit', (event) => {
  event.preventDefault();
  const payload = {
    username: $('register-username').value.trim(),
    email: $('register-email').value.trim(),
    password: $('register-password').value
  };
  submitAuth('/api/auth/register', payload, 'accountCreated');
});

$('auth-login').addEventListener('submit', (event) => {
  event.preventDefault();
  const payload = {
    username: $('login-username').value.trim(),
    password: $('login-password').value
  };
  submitAuth('/api/auth/login', payload, 'loggedIn');
});

async function signOut() {
  try {
    await postJSON('/api/auth/logout', {});
    showToast(t('loggedOut'));
  } catch (error) {
    showToast(errorText(error));
  }
  authDialog.close();
  await refreshAuth();
}
$('auth-logout').addEventListener('click', signOut);
$('logout-admin').addEventListener('click', signOut);
$('auth-admin-link').addEventListener('click', () => { authDialog.close(); setView('admin'); });

async function loadUsers() {
  try {
    const response = await fetch('/api/admin/users');
    const data = await response.json();
    if (!response.ok) { $('admin-status').textContent = errorText(new Error(data.error)); return; }
    const container = $('admin-users');
    container.replaceChildren();
    data.users.forEach((account) => {
      const row = el('div', 'user-row');
      row.append(el('span', '', `${account.username} · ${account.email}`));
      row.append(el('span', 'role-pill' + (account.role === 'admin' ? ' admin' : ''), t(account.role === 'admin' ? 'admin' : 'user')));
      container.append(row);
    });
  } catch (error) {
    $('admin-status').textContent = t('loadFailed');
  }
}

const SCOPE_KEYS = {
  shamela: 'scopeShamela', dorar: 'scopeDorar',
  hadith: 'scopeHadith', quote: 'scopeQuote', all: 'scopeAll'
};

function formatDate(seconds) {
  const date = new Date(Number(seconds) * 1000);
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString();
}

async function loadUsersTable() {
  const body = $('users-body');
  const status = $('users-status');
  status.textContent = t('loadingStats');
  try {
    const response = await fetch('/api/admin/users');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || t('loadFailed'));
    body.replaceChildren();
    data.users.forEach((account) => {
      const row = el('tr');
      row.append(el('td', '', account.username));
      row.append(el('td', '', account.email));
      row.append(el('td', 'pill-cell',
        el('span', 'role-pill' + (account.role === 'admin' ? ' admin' : ''),
          t(account.role === 'admin' ? 'admin' : 'user'))));
      row.append(el('td', '', t(account.provider === 'google' ? 'google' : 'local')));
      row.append(el('td', 'history-meta', formatDate(account.created_at)));
      body.append(row);
    });
    if (!data.users.length) {
      const row = el('tr');
      const cell = el('td', 'muted', t('noRecords'));
      cell.colSpan = 5;
      row.append(cell);
      body.append(row);
    }
    status.textContent = '';
  } catch (error) {
    status.textContent = errorText(error) || t('loadFailed');
  }
}

async function loadHistory() {
  const container = $('history-list');
  const status = $('history-status');
  status.textContent = t('loadingStats');
  try {
    const response = await fetch('/api/history');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || t('loadFailed'));
    container.replaceChildren();
    if (!data.history.length) {
      container.append(el('p', 'muted', t('noHistory')));
    } else {
      data.history.forEach((item) => {
        const row = el('div', 'history-row');
        row.append(el('span', 'history-query', item.query));
        const key = SCOPE_KEYS[item.scope];
        const meta = [key ? t(key) : item.scope,
          t('found', { count: item.result_count }), formatDate(item.created_at)]
          .filter(Boolean).join(' · ');
        row.append(el('span', 'history-meta', meta));
        container.append(row);
      });
    }
    status.textContent = '';
  } catch (error) {
    status.textContent = errorText(error) || t('loadFailed');
  }
}

$('clear-history').addEventListener('click', async () => {
  try {
    await postJSON('/api/history/clear', {});
    showToast(t('historyCleared'));
    loadHistory();
  } catch (error) {
    $('history-status').textContent = errorText(error);
  }
});

$('hadith-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form));
  payload.verified = payload.verified === 'true';
  try {
    const data = await postJSON('/api/admin/hadith', payload);
    $('admin-status').textContent = data.message || t('addHadith');
    form.reset();
  } catch (error) {
    $('admin-status').textContent = errorText(error);
  }
});

$('refresh-records').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/admin/records');
    const data = await response.json();
    if (!response.ok) { $('admin-status').textContent = errorText(new Error(data.error)); return; }
    const container = $('admin-records');
    container.replaceChildren();
    if (!data.records.length) container.append(el('p', 'muted', t('noRecords')));
    for (const record of data.records) {
      const line = el('div', 'record');
      const kind = record.kind === 'hadith' ? t('wordHadith') : t('wordQuote');
      line.append(el('span', '', `#${record.id} · ${kind} · ${record.book} · ${String(record.passage).slice(0, 70)}…`));
      const remove = el('button', 'copy-btn', t('deleteConfirm').replace('؟', '').replace('?', ''));
      remove.type = 'button';
      remove.addEventListener('click', async () => {
        if (!window.confirm(t('deleteConfirm'))) return;
        try {
          await postJSON('/api/admin/delete', { id: record.id });
          line.remove();
        } catch (error) {
          $('admin-status').textContent = errorText(error);
        }
      });
      line.append(remove);
      container.append(line);
    }
  } catch (error) {
    $('admin-status').textContent = t('loadFailed');
  }
});

applyLanguage(lang);
handleAuthRedirect();
refreshAuth();
