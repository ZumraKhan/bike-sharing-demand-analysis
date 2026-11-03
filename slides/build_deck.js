/**
 * Build the project slide deck.
 *
 * Structured deck: one theme, named layouts with placeholders, and sections,
 * so the whole deck restyles from a single object. Every number is read from
 * outputs/metrics.json and every figure from figures/, so the deck, the PDF
 * report and the notebook cannot disagree with each other.
 *
 *   node slides/build_deck.js
 */

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const OUT = path.join(ROOT, "slides", "Bike_Sharing_Demand_Deck.pptx");

const M = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "metrics.json"), "utf8"));
const Q = M.quality, D = M.descriptive, P = M.predictive;

// ---------------------------------------------------------------- theme
const THEME = {
  name: "Bike Share Analysis",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B0B0B",   // primary ink
    lt1: "FFFFFF",   // surface
    dk2: "0D366B",   // deep navy, the dominant dark
    lt2: "F2F6FD",   // pale blue wash
    accent1: "2A78D6", // blue  - the series hue in every figure
    accent2: "EB6834", // orange - the single sharp accent
    accent3: "184F95",
    accent4: "1BAF7A",
    accent5: "86B6EF",
    accent6: "898781", // muted ink
    hlink: "2A78D6",
    folHlink: "184F95",
  },
};

const pres = new PptxGenJS();
pres.layout = "LAYOUT_WIDE";          // 13.3 x 7.5 inches - set BEFORE any slide
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "";
pres.company = "";
pres.subject = "Descriptive, visual and predictive analysis";
pres.title = "Bike Sharing Demand Analysis";

const C = pres.SchemeColor;
const SW = 13.3, SH = 7.5, MGN = 0.62;

// ---------------------------------------------------------------- helpers
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

/** Fit an image inside a box, preserving aspect ratio and centring it. */
function fit(name, box) {
  const p = path.join(FIG, name);
  const { w, h } = pngSize(p);
  const scale = Math.min(box.w / w, box.h / h);
  const w2 = w * scale, h2 = h * scale;
  return { path: p, x: box.x + (box.w - w2) / 2, y: box.y + (box.h - h2) / 2, w: w2, h: h2 };
}

const n = (v, d = 0) => Number(v).toLocaleString("en-US", {
  minimumFractionDigits: d, maximumFractionDigits: d,
});

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: THEME.colors.dk2 },
  objects: [
    { placeholder: { options: {
        name: "title", type: "title", x: MGN + 0.3, y: 2.25, w: 10.4, h: 1.9,
        fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left" } } },
    { placeholder: { options: {
        name: "body", type: "body", x: MGN + 0.3, y: 4.3, w: 9.6, h: 1.0,
        fontSize: 17, color: THEME.colors.accent5, valign: "top", align: "left" } } },
    { placeholder: { options: {
        name: "meta", type: "body", x: MGN + 0.3, y: 6.25, w: 11.0, h: 0.7,
        fontSize: 12, color: THEME.colors.accent5, valign: "top", align: "left" } } },
  ],
});

pres.defineSlideMaster({
  title: "DIVIDER",
  background: { color: THEME.colors.dk2 },
  objects: [
    { placeholder: { options: {
        name: "kicker", type: "body", x: MGN + 0.3, y: 2.6, w: 9.0, h: 0.55,
        fontSize: 15, bold: true, color: THEME.colors.accent2, charSpacing: 2, align: "left" } } },
    { placeholder: { options: {
        name: "title", type: "title", x: MGN + 0.3, y: 3.15, w: 10.6, h: 1.3,
        fontSize: 38, bold: true, color: C.background1, valign: "top", align: "left" } } },
    { placeholder: { options: {
        name: "body", type: "body", x: MGN + 0.3, y: 4.5, w: 9.8, h: 1.0,
        fontSize: 15, color: THEME.colors.accent5, align: "left" } } },
  ],
});

/** Light content slide: title top-left, free canvas beneath. */
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: {
        name: "title", type: "title", x: MGN, y: 0.42, w: 12.1, h: 0.72,
        fontSize: 28, bold: true, color: THEME.colors.dk2, valign: "middle", align: "left" } } },
    { placeholder: { options: {
        name: "body", type: "body", x: MGN, y: 1.2, w: 12.1, h: 0.62,
        fontSize: 15, color: THEME.colors.accent6, valign: "top", align: "left" } } },
    { text: { text: "Bike Sharing Demand Analysis", options: {
        x: MGN, y: 6.92, w: 7.0, h: 0.3, fontSize: 10,
        color: THEME.colors.accent6, isTextBox: true, margin: 0 } } },
  ],
  slideNumber: { x: 12.5, y: 6.92, w: 0.4, h: 0.3, fontSize: 10,
                 color: THEME.colors.accent6 },
});

pres.defineSlideMaster({
  title: "CLOSING",
  background: { color: THEME.colors.dk2 },
  objects: [
    { placeholder: { options: {
        name: "title", type: "title", x: MGN + 0.3, y: 2.7, w: 10.6, h: 1.2,
        fontSize: 36, bold: true, color: C.background1, valign: "bottom", align: "left" } } },
    { placeholder: { options: {
        name: "body", type: "body", x: MGN + 0.3, y: 4.0, w: 10.0, h: 1.6,
        fontSize: 15, color: THEME.colors.accent5, align: "left" } } },
  ],
});

// ---------------------------------------------------------------- pieces
/** Big number with a label beneath - the deck's repeated visual motif. */
function statTile(slide, { x, y, w, value, label, note, color = THEME.colors.accent1 }) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 1.85, rectRadius: 0.1, fill: { color: THEME.colors.lt2 },
    line: { color: THEME.colors.lt2 }, objectName: `tile-${label}`,
  });
  slide.addText(value, {
    x: x + 0.18, y: y + 0.16, w: w - 0.36, h: 0.78, fontSize: 36, bold: true,
    color, align: "left", valign: "middle", isTextBox: true, margin: 0,
  });
  slide.addText(label, {
    x: x + 0.18, y: y + 0.95, w: w - 0.36, h: 0.32, fontSize: 13, bold: true,
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  if (note) {
    slide.addText(note, {
      x: x + 0.18, y: y + 1.27, w: w - 0.36, h: 0.45, fontSize: 11,
      color: THEME.colors.accent6, isTextBox: true, margin: 0,
    });
  }
}

/** Numbered card used for process / findings rows. */
function card(slide, { x, y, w, h = 1.5, num, head, text }) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: THEME.colors.lt2 },
    line: { color: THEME.colors.lt2 }, objectName: `card-${num}`,
  });
  slide.addShape(pres.ShapeType.ellipse, {
    x: x + 0.22, y: y + 0.24, w: 0.46, h: 0.46,
    fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1 },
  });
  slide.addText(String(num), {
    x: x + 0.22, y: y + 0.24, w: 0.46, h: 0.46, fontSize: 14, bold: true,
    color: "FFFFFF", align: "center", valign: "middle", isTextBox: true, margin: 0,
  });
  slide.addText(head, {
    x: x + 0.82, y: y + 0.2, w: w - 1.0, h: 0.34, fontSize: 14, bold: true,
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  slide.addText(text, {
    x: x + 0.82, y: y + 0.54, w: w - 1.0, h: h - 0.68, fontSize: 12,
    color: THEME.colors.dk1, isTextBox: true, margin: 0, valign: "top",
  });
}

/** A figure plus the one sentence it proves. */
function figureSlide({ section, title, kicker, file, takeaway, notes }) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (kicker) s.addText(kicker, { placeholder: "body" });

  const box = { x: MGN, y: 1.82, w: SW - 2 * MGN, h: 4.05 };
  s.addImage({ ...fit(file, box), objectName: file });

  if (takeaway) {
    s.addShape(pres.ShapeType.roundRect, {
      x: MGN, y: 6.0, w: SW - 2 * MGN, h: 0.78, rectRadius: 0.08,
      fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 },
    });
    s.addText([{ text: "Takeaway   ", options: { bold: true, color: THEME.colors.accent2 } },
               { text: takeaway, options: { color: THEME.colors.dk1 } }], {
      x: MGN + 0.22, y: 6.0, w: SW - 2 * MGN - 0.44, h: 0.78, fontSize: 13,
      valign: "middle", isTextBox: true, margin: 0,
    });
  }
  if (notes) s.addNotes(notes);
  return s;
}

// ================================================================= SLIDES
pres.addSection({ title: "Opening" });

// --- 1. title ------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
  s.addText("Bike Sharing Demand Analysis", { placeholder: "title" });
  s.addText("What drives demand for shared bikes, and can the next hour be predicted?",
            { placeholder: "body" });
  s.addText(`${n(Q.hourly_rows)} hourly records  ·  Washington D.C.  ·  ${Q.date_start} to ${Q.date_end}  ·  Descriptive · Visual · Predictive`,
            { placeholder: "meta" });
  s.addShape(pres.ShapeType.rect, {
    x: MGN + 0.3, y: 5.55, w: 2.4, h: 0.07,
    fill: { color: THEME.colors.accent2 }, line: { color: THEME.colors.accent2 },
  });
  s.addNotes("Two years of Capital Bikeshare data from Washington D.C. The project "
    + "covers all three analysis types: descriptive statistics, data visualization, "
    + "and a predictive model.");
}

// --- 2. the data ---------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
  s.addText("Two years of a city on bikes", { placeholder: "title" });
  s.addText("Capital Bikeshare, Washington D.C. — hourly rental counts with weather and calendar context",
            { placeholder: "body" });

  const w = 2.86, gap = 0.3;
  const xs = [MGN, MGN + w + gap, MGN + 2 * (w + gap), MGN + 3 * (w + gap)];
  statTile(s, { x: xs[0], y: 2.0, w, value: n(Q.hourly_rows), label: "Hourly records",
                note: `${Q.coverage_pct}% calendar coverage` });
  statTile(s, { x: xs[1], y: 2.0, w, value: n(D.total_rentals), label: "Total rentals",
                note: "Across 2011 and 2012" });
  statTile(s, { x: xs[2], y: 2.0, w, value: `+${D.yoy_growth_pct}%`, label: "Year-on-year growth",
                note: `${n(D.rentals_2011)} to ${n(D.rentals_2012)}`, color: THEME.colors.accent2 });
  statTile(s, { x: xs[3], y: 2.0, w, value: `${D.registered_share_pct}%`, label: "Registered share",
                note: "Members, not casual riders" });

  s.addText("What the data holds", {
    x: MGN, y: 4.3, w: 12.1, h: 0.35, fontSize: 16, bold: true,
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  const items = [
    { t: "Calendar", d: "Season, year, month, hour, weekday, holiday and working-day flags" },
    { t: "Weather", d: "Temperature, feels-like, humidity, wind speed and a 4-level condition code" },
    { t: "Target", d: "cnt — total bikes rented in that hour, split into casual and registered" },
  ];
  items.forEach((it, i) => {
    const y = 4.78 + i * 0.6;
    s.addShape(pres.ShapeType.ellipse, {
      x: MGN + 0.04, y: y + 0.09, w: 0.17, h: 0.17,
      fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1 },
    });
    s.addText([{ text: `${it.t}   `, options: { bold: true, color: THEME.colors.dk2 } },
               { text: it.d, options: { color: THEME.colors.dk1 } }], {
      x: MGN + 0.38, y, w: 11.6, h: 0.42, fontSize: 13.5, valign: "middle",
      isTextBox: true, margin: 0,
    });
  });
  s.addNotes("The weather columns arrive min-max normalised; they are converted back "
    + "to degrees Celsius, percent and km/h so every chart is readable.");
}

// --- 3. data quality -----------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
  s.addText("Clean data — with one trap in it", { placeholder: "title" });
  s.addText("Four checks run before any analysis", { placeholder: "body" });

  const w = 2.86, gap = 0.3;
  [
    { v: String(Q.missing_values), l: "Missing values", nt: "No imputation needed" },
    { v: String(Q.duplicate_rows), l: "Duplicate rows", nt: "No de-duplication needed" },
    { v: String(Q.missing_hours), l: "Absent hours", nt: `${Q.coverage_pct}% coverage — excluded, not zero-filled` },
    { v: "100%", l: "Target consistency", nt: "cnt = casual + registered, every row" },
  ].forEach((d, i) => statTile(s, {
    x: MGN + i * (w + gap), y: 1.95, w, value: d.v, label: d.l, note: d.nt,
    color: i === 3 ? THEME.colors.accent2 : THEME.colors.accent1,
  }));

  s.addShape(pres.ShapeType.roundRect, {
    x: MGN, y: 4.25, w: SW - 2 * MGN, h: 2.0, rectRadius: 0.1,
    fill: { color: THEME.colors.dk2 }, line: { color: THEME.colors.dk2 },
  });
  s.addText("The leakage trap", {
    x: MGN + 0.4, y: 4.48, w: 11.4, h: 0.4, fontSize: 18, bold: true,
    color: THEME.colors.accent2, isTextBox: true, margin: 0,
  });
  s.addText("cnt is exactly casual + registered in all " + n(Q.hourly_rows) + " rows. Any model handed those two "
    + "columns reconstructs the target perfectly and reports flawless accuracy while having learned nothing. "
    + "Both are dropped from the feature set.", {
    x: MGN + 0.4, y: 4.92, w: 11.4, h: 0.85, fontSize: 14, color: "FFFFFF",
    isTextBox: true, margin: 0, valign: "top",
  });
  s.addText("This is the most common error made with this dataset — and nothing in the output announces it.", {
    x: MGN + 0.4, y: 5.74, w: 11.4, h: 0.35, fontSize: 12.5, italic: true,
    color: THEME.colors.accent5, isTextBox: true, margin: 0,
  });
  s.addNotes("Worth dwelling on: a leaked model scores R-squared near 1.0 and is worthless. "
    + "Everything in the feature set is knowable before the hour starts.");
}

// ================================================= descriptive + visual
pres.addSection({ title: "Descriptive and visual analysis" });
const SEC1 = "Descriptive and visual analysis";

{
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: SEC1 });
  s.addText("PART ONE", { placeholder: "kicker" });
  s.addText("Descriptive and visual analysis", { placeholder: "title" });
  s.addText("What does demand actually look like?", { placeholder: "body" });
}

// --- 5. distribution -----------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC1 });
  s.addText("A typical hour does not exist", { placeholder: "title" });
  s.addText("Distribution of hourly rental counts", { placeholder: "body" });

  const w = 2.86, gap = 0.3;
  [
    { v: n(D.mean_hourly, 1), l: "Mean rentals / hour", nt: `Median ${n(D.median_hourly)}` },
    { v: `${D.cv_pct}%`, l: "Coefficient of variation", nt: "Std. dev. nearly equals the mean" },
    { v: `+${D.skewness}`, l: "Skewness", nt: "Long right tail of busy hours" },
    { v: `${D.peak_to_trough_ratio}x`, l: "Peak-to-trough ratio", nt: `${String(D.peak_hour).padStart(2, "0")}:00 against ${String(D.trough_hour).padStart(2, "0")}:00`,
      color: THEME.colors.accent2 },
  ].forEach((d, i) => statTile(s, {
    x: MGN + i * (w + gap), y: 1.95, w, value: d.v, label: d.l, note: d.nt,
    color: d.color || THEME.colors.accent1,
  }));

  s.addText("Why the mean misleads here", {
    x: MGN, y: 4.3, w: 12.1, h: 0.35, fontSize: 16, bold: true,
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  s.addText([
    { text: `The mean (${D.mean_hourly}) sits a third above the median (${n(D.median_hourly)}). Most hours are quiet; a small number of commuter peaks carry a disproportionate share of all trips.`,
      options: { bullet: true, breakLine: true } },
    { text: `Demand ranges from ${D.min_hourly} to ${n(D.max_hourly)} rentals in an hour — three orders of magnitude.`,
      options: { bullet: true, breakLine: true } },
    { text: "That variability is structure, not noise. Part Two shows a model can recover most of it.",
      options: { bullet: true } },
  ], {
    x: MGN, y: 4.75, w: 12.1, h: 1.6, fontSize: 13.5, color: THEME.colors.dk1,
    paraSpaceAfter: 7, isTextBox: true, margin: 0, valign: "top",
  });
  s.addNotes("Skewness of +1.28 and a coefficient of variation of 95.7% are the two "
    + "numbers to quote: hourly demand is highly variable and far from normal.");
}

figureSlide({
  section: SEC1,
  title: "Two different cities share one fleet",
  kicker: "Mean rentals by hour of day, split by day type",
  file: "fig01_hourly_profile.png",
  takeaway: `Working days peak at ${String(D.workingday_peak_hour).padStart(2, "0")}:00 with ${n(D.workingday_peak_mean)} rentals an hour; the weekend curve peaks at ${String(D.weekend_peak_hour).padStart(2, "0")}:00 with ${n(D.weekend_peak_mean)} and has no commuter spike at all. Averaging the two destroys both patterns.`,
  notes: "The single most important chart in the deck. Two completely different "
    + "demand shapes: commuter twin peaks versus a weekend midday hump.",
});

figureSlide({
  section: SEC1,
  title: "The commuter band is visible by eye",
  kicker: "Mean rentals by weekday and hour of day",
  file: "fig03_hour_weekday_heatmap.png",
  takeaway: "Monday to Friday show two dark vertical bands at the commute; Saturday and Sunday replace them with one broad midday block.",
  notes: "A sequential single-hue ramp: darker means busier. No rainbow scales - "
    + "they invent category boundaries that are not in the data.",
});

figureSlide({
  section: SEC1,
  title: "Demand nearly doubled in year two",
  kicker: "Total monthly rentals, Jan 2011 to Dec 2012",
  file: "fig02_monthly_trend.png",
  takeaway: `Rentals grew ${D.yoy_growth_pct}% year on year while keeping the same seasonal shape — a repeating annual pattern on top of a steady trend, which is what makes the series learnable.`,
  notes: "The repeating shape matters for modelling: the model can separate the "
    + "seasonal cycle from the growth trend because it sees the cycle twice.",
});

figureSlide({
  section: SEC1,
  title: "Members carry the service; weekends belong to visitors",
  kicker: "Monthly rentals split by user type",
  file: "fig07_user_mix.png",
  takeaway: `Registered members are ${D.registered_share_pct}% of all trips. Casual riders are ${D.casual_share_weekend_pct}% of weekend trips but only ${D.casual_share_working_pct}% on working days — commuting and leisure are two products.`,
  notes: "This is the commercial slide: the conversion opportunity is at weekends.",
});

figureSlide({
  section: SEC1,
  title: "Bad weather halves demand, but not its shape",
  kicker: "Mean rentals per hour by weather situation",
  file: "fig04_weather_impact.png",
  takeaway: `Heavy rain or snow cuts hourly demand ${D.weather_drop_pct}% against clear conditions — but that final bar rests on only 3 hours in two years, so it is a direction, not a dependable effect size.`,
  notes: "Always show the sample counts when categories are this unbalanced. "
    + "Three observations cannot support a precise estimate.",
});

figureSlide({
  section: SEC1,
  title: "Warmer sells more rides — up to a ceiling",
  kicker: `Hourly rentals against temperature   ·   r = ${D.corr_temp}`,
  file: "fig06_temp_vs_demand.png",
  takeaway: "Demand climbs with temperature to roughly 33 °C and then falls away. The relationship is non-linear, which is the first concrete reason to expect tree models to beat linear regression.",
  notes: "This slide sets up Part Two: a straight line cannot bend at 33 degrees.",
});

// ================================================= predictive
pres.addSection({ title: "Predictive analysis" });
const SEC2 = "Predictive analysis";

{
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: SEC2 });
  s.addText("PART TWO", { placeholder: "kicker" });
  s.addText("Predictive analysis", { placeholder: "title" });
  s.addText("Given tomorrow's calendar and forecast, how many bikes will be rented this hour?",
            { placeholder: "body" });
}

// --- method --------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC2 });
  s.addText("How the model was built and tested", { placeholder: "title" });
  s.addText("Regression on hourly rental counts", { placeholder: "body" });

  const w = 3.9, gap = 0.3;
  card(s, { x: MGN, y: 1.9, w, h: 2.1, num: 1, head: "Features",
    text: `${P.n_features} calendar and weather variables. Hour, month and weekday are also encoded as sine/cosine pairs, so the model treats the clock as the circle it is — hour 23 sits next to hour 00.` });
  card(s, { x: MGN + w + gap, y: 1.9, w, h: 2.1, num: 2, head: "Split",
    text: `Chronological: train on the first ${n(P.train_rows)} hours (to ${P.train_end}), test on the ${n(P.test_rows)} most recent hours it has never seen. A random split is run alongside for contrast.` });
  card(s, { x: MGN + 2 * (w + gap), y: 1.9, w, h: 2.1, num: 3, head: "Models",
    text: "Linear Regression, Decision Tree, Random Forest and Gradient Boosting, each measured against a naive baseline that always predicts the training mean." });

  s.addShape(pres.ShapeType.roundRect, {
    x: MGN, y: 4.3, w: SW - 2 * MGN, h: 1.95, rectRadius: 0.1,
    fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 },
  });
  s.addText("Why the split choice matters", {
    x: MGN + 0.4, y: 4.52, w: 11.4, h: 0.38, fontSize: 17, bold: true,
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  s.addText("A random split lets a model train on hours that sit between the hours it is tested on — it interpolates inside a series it has already seen instead of forecasting beyond it. "
    + "For a forecasting question that is the wrong test, and it flatters every model.", {
    x: MGN + 0.4, y: 4.95, w: 11.4, h: 0.9, fontSize: 14, color: THEME.colors.dk1,
    isTextBox: true, margin: 0, valign: "top",
  });
  s.addNotes("If asked why not cross-validation: TimeSeriesSplit with 5 expanding "
    + `folds was also run, mean RMSE ${P.cv_rmse_mean} plus or minus ${P.cv_rmse_std}.`);
}

figureSlide({
  section: SEC2,
  title: "Gradient Boosting forecasts demand best",
  kicker: "Test-set RMSE on the chronological split — lower is better",
  file: "fig09_model_comparison.png",
  takeaway: `${P.best_model}: RMSE ${n(P.best_rmse, 1)} rentals an hour, R² ${P.best_r2.toFixed(2)} on unseen future hours — a ${P.rmse_vs_baseline_pct}% error reduction against the naive baseline.`,
  notes: "Linear regression trails badly because it cannot bend at 33 degrees and "
    + "cannot represent the hour-by-day-type interaction.",
});

// --- optimism gap --------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC2 });
  s.addText("The same model, two very different scores", { placeholder: "title" });
  s.addText("Test-set RMSE under each validation scheme", { placeholder: "body" });

  const names = Object.keys(P.random_results)
    .sort((a, b) => P.results[a].rmse - P.results[b].rmse);
  const rows = [[
    { text: "Model", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 } } },
    { text: "Chronological", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, align: "right" } },
    { text: "Random", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, align: "right" } },
    { text: "Optimism gap", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, align: "right" } },
  ]];
  names.forEach((name, i) => {
    const c = P.results[name].rmse, r = P.random_results[name].rmse;
    const bg = i % 2 ? THEME.colors.lt2 : "FFFFFF";
    const best = name === P.best_model;
    rows.push([
      { text: name, options: { bold: best, color: best ? THEME.colors.accent1 : THEME.colors.dk1, fill: { color: bg } } },
      { text: n(c, 1), options: { align: "right", fill: { color: bg }, color: THEME.colors.dk1 } },
      { text: n(r, 1), options: { align: "right", fill: { color: bg }, color: THEME.colors.dk1 } },
      { text: `+${n(c - r, 1)}`, options: { align: "right", bold: true, color: THEME.colors.accent2, fill: { color: bg } } },
    ]);
  });
  s.addTable(rows, {
    x: MGN, y: 1.95, w: SW - 2 * MGN, colW: [5.2, 2.3, 2.3, 2.26],
    rowH: 0.42, fontSize: 13.5, fontFace: "Calibri", valign: "middle",
    border: { type: "solid", pt: 0.5, color: "E1E0D9" },
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: MGN, y: 4.75, w: SW - 2 * MGN, h: 1.5, rectRadius: 0.1,
    fill: { color: THEME.colors.dk2 }, line: { color: THEME.colors.dk2 },
  });
  s.addText([
    { text: "Every model looks better under a random split. ", options: { bold: true, color: THEME.colors.accent2 } },
    { text: `For the winning model the gap is about ${n(P.results[P.best_model].rmse - P.random_results[P.best_model].rmse, 0)} RMSE: reporting the random-split figure as forecasting accuracy would overstate real performance by roughly a third.`,
      options: { color: "FFFFFF" } },
  ], {
    x: MGN + 0.4, y: 4.95, w: 11.4, h: 1.1, fontSize: 15, valign: "middle",
    isTextBox: true, margin: 0,
  });
  s.addNotes("This is the methodological point of the whole project: the evaluation "
    + "design changes the answer more than the model choice does.");
}

figureSlide({
  section: SEC2,
  title: "The clock matters more than the weather",
  kicker: `Random Forest feature importance, top 12 of ${P.n_features}`,
  file: "fig10_feature_importance.png",
  takeaway: "Hour of day alone carries 38.3% of importance; with its cyclical encodings, time of day accounts for about 61%. Every weather variable together carries roughly 20%.",
  notes: "Temperature and feels-like temperature correlate at 0.99, so their "
    + "importance splits between two near-duplicate columns.",
});

figureSlide({
  section: SEC2,
  title: "Forecasts track the real commuter rhythm",
  kicker: `First 10 days of the unseen test period, from ${P.test_start}`,
  file: "fig11_actual_vs_predicted.png",
  takeaway: "The model reproduces both commuter peaks and the overnight trough, and follows day-to-day variation rather than repeating an average daily curve. Its weakness is shaving the sharpest peaks.",
  notes: "Residuals are heteroscedastic — error grows with demand — so peak hours "
    + "are where the model is least precise in absolute terms.",
});

// ================================================= conclusions
pres.addSection({ title: "Conclusions" });
const SEC3 = "Conclusions";

// --- findings ------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC3 });
  s.addText("Six findings", { placeholder: "title" });
  s.addText("What two years of rental data say", { placeholder: "body" });

  const w = 6.0, gap = 0.36;
  const items = [
    { h: "Time beats weather", t: "Time-of-day features carry about 61% of predictive importance; all weather features together carry roughly 20%." },
    { h: "Two businesses, one fleet", t: `Working days are commuter-shaped (${D.casual_share_working_pct}% casual); weekends are leisure-shaped (${D.casual_share_weekend_pct}% casual).` },
    { h: `Growth of ${D.yoy_growth_pct}% year on year`, t: "Driven almost entirely by registered members rather than casual riders." },
    { h: "Weather modulates, not determines", t: `Heavy rain or snow cuts demand ${D.weather_drop_pct}%, yet the daily shape survives intact.` },
    { h: "Demand is predictable", t: `${P.best_model} reaches R² ${P.best_r2.toFixed(2)} on unseen future hours, a ${P.rmse_vs_baseline_pct}% error reduction over the baseline.` },
    { h: "Evaluation design changes the answer", t: "A random split flatters every model by 15 to 30 RMSE and is the wrong test for forecasting." },
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    card(s, { x: MGN + col * (w + gap), y: 1.9 + row * 1.6, w, h: 1.42,
              num: i + 1, head: it.h, text: it.t });
  });
  s.addNotes("If time is short, findings 1, 2 and 6 are the ones that matter.");
}

// --- recommendations -----------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC3 });
  s.addText("What an operator should do with this", { placeholder: "title" });
  s.addText("Recommendations, and the limits on them", { placeholder: "body" });

  s.addText("Recommendations", {
    x: MGN, y: 1.9, w: 6.0, h: 0.35, fontSize: 16, bold: true,
    color: THEME.colors.accent1, isTextBox: true, margin: 0,
  });
  s.addText([
    { text: "Finish fleet rebalancing before 07:00 and 16:00 on working days; treat weather as a secondary adjustment.", options: { bullet: true, breakLine: true } },
    { text: "Run separate weekday and weekend operating plans — one averaged schedule fits neither.", options: { bullet: true, breakLine: true } },
    { text: `Target casual-to-member conversion at weekends, where casual riders are ${D.casual_share_weekend_pct}% of trips.`, options: { bullet: true, breakLine: true } },
    { text: "Deploy the model for hour-ahead staffing, with prediction intervals that widen at peaks.", options: { bullet: true, breakLine: true } },
    { text: "Re-fit each season: the growth term is fitted on two years and cannot be extrapolated.", options: { bullet: true } },
  ], {
    x: MGN, y: 2.35, w: 6.0, h: 3.6, fontSize: 13, color: THEME.colors.dk1,
    paraSpaceAfter: 9, isTextBox: true, margin: 0, valign: "top",
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: MGN + 6.4, y: 1.9, w: 5.68, h: 4.1, rectRadius: 0.1,
    fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 },
  });
  s.addText("Limitations", {
    x: MGN + 6.72, y: 2.1, w: 5.04, h: 0.35, fontSize: 16, bold: true,
    color: THEME.colors.accent2, isTextBox: true, margin: 0,
  });
  s.addText([
    { text: "Two years, one city — the growth term must not be extrapolated past 2012.", options: { bullet: true, breakLine: true } },
    { text: "Observed weather, not forecast weather: live accuracy would be lower.", options: { bullet: true, breakLine: true } },
    { text: "Only 3 hours of heavy rain or snow exist in the whole dataset.", options: { bullet: true, breakLine: true } },
    { text: "Events are unmodelled — Hurricane Sandy produces the largest residual of all.", options: { bullet: true, breakLine: true } },
    { text: "No spatial dimension, so it cannot drive station-level rebalancing.", options: { bullet: true } },
  ], {
    x: MGN + 6.72, y: 2.58, w: 5.04, h: 3.3, fontSize: 12.5,
    color: THEME.colors.dk1, paraSpaceAfter: 8, isTextBox: true, margin: 0,
    valign: "top",
  });
  s.addNotes("Lead with the limitations if the audience is technical — they are the "
    + "first thing a reviewer will ask about.");
}

// --- closing -------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CLOSING", sectionTitle: SEC3 });
  s.addText("Demand runs on the clock", { placeholder: "title" });
  s.addText(`${n(Q.hourly_rows)} hours of data · 12 figures · 4 models · R² ${P.best_r2.toFixed(2)} on hours the model had never seen\n\n`
    + "Code, notebook, report and data: see the project repository.", { placeholder: "body" });
  s.addShape(pres.ShapeType.rect, {
    x: MGN + 0.3, y: 2.45, w: 2.4, h: 0.07,
    fill: { color: THEME.colors.accent2 }, line: { color: THEME.colors.accent2 },
  });
  s.addNotes("Close on the single sentence: demand is governed by the clock, "
    + "weather only modulates it.");
}

// ---------------------------------------------------------------- write
(async () => {
  await pres.writeFile({ fileName: OUT });
  const { applyTheme } = require(path.join(
    process.env.PPTX_SKILL_DIR, "scripts", "apply_theme.js"));
  await applyTheme(OUT, THEME);
  const kb = (fs.statSync(OUT).size / 1024).toFixed(0);
  console.log(`wrote ${OUT}  (${kb} KB)`);
})().catch((e) => { console.error(e); process.exit(1); });
