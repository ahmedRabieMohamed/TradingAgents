/*
 * Smart Picks column classification — applied across the redesign.
 *
 *   primary      (always visible in the table)
 *     - rank, ticker, company_name (+ sector subtitle), signal, combined_score,
 *       volatility_regime_tag (badge), bullish_engines/total_engines, action button
 *
 *   expanded     (inside the AntD expandable row, rendered by PickRowExpanded)
 *     - mc_probability, mc_expected, mc_best_case, mc_worst_case
 *     - sr_current / sr_support / sr_resistance / sr_risk_reward / sr_upside_pct / sr_downside_pct
 *     - momentum_trend, momentum_roc_5d, momentum_roc_20d
 *     - mr_distance_pct, mr_is_oversold, mr_is_overbought
 *     - bb_band_width, corr_sector / corr_peers_*
 *     - volume_ratio (with volume_is_real flag)
 *     - per-engine score bars + verdict tags for all engines
 *
 *   drawer       (full per-pick detail in PickDetailDrawer; finished in US5)
 *     - everything from `expanded` plus per-engine weight % and contribution-to-combined breakdown,
 *       full reason text per engine, score-breakdown panel
 *
 * No metric should be classified as drawer-only — every metric must also be
 * reachable from the in-page expanded row so traders can compare picks
 * side-by-side without opening a drawer.
 */

// PickRow itself is rendered as cells inside the AntD Table; this file
// exports helpers that the columns config consumes. Keeping the inventory
// comment here (instead of in SmartPicks.tsx) so it stays close to the
// component that drives the row layout.

export {};
