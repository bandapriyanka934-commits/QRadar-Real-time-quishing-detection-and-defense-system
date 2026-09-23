import 'package:flutter/material.dart';

/// Centralized QRadar Design System & Color Palette
/// Dark Enterprise Cybersecurity: Deep Navy + Slate Panels + Electric Blue Accents
class QRadarColors {
  // Foundation Palette
  static const Color primaryBackground = Color(0xFF0B1220); // #0B1220 - Deep Navy Foundation
  static const Color deepNavy = Color(0xFF0B1220);          // Alias
  static const Color sidebar = Color(0xFF0F172A);           // #0F172A - Sidebar Slate Dark
  static const Color surface = Color(0xFF162235);           // #162235 - Card / Panel Surface
  static const Color surfaceElevated = Color(0xFF1E293B);   // #1E293B - Elevated / Hover Surface
  static const Color border = Color(0xFF334155);            // #334155 - Subtle Enterprise Border
  static const Color borderSubtle = Color(0xFF1E293B);      // #1E293B
  static const Color borderLight = Color(0xFF64748B);       // #64748B - Dashed / Highlight Border

  // Electric Blue & Brand Accents
  static const Color primaryBlue = Color(0xFF38BDF8);       // #38BDF8 - Primary QRadar Blue
  static const Color secondaryBlue = Color(0xFF60A5FA);     // #60A5FA - Secondary Blue
  static const Color accentCyan = Color(0xFF22D3EE);        // #22D3EE - Cyan Accent

  // Typography Tokens
  static const Color textPrimary = Color(0xFFF8FAFC);       // #F8FAFC - Primary Text / Headings
  static const Color textSecondary = Color(0xFF94A3B8);     // #94A3B8 - Secondary Text / Metadata
  static const Color textSubtle = Color(0xFFCBD5E1);        // #CBD5E1 - Secondary Headings / Nav
  static const Color textMuted = Color(0xFF64748B);         // #64748B - Placeholders / Subdued
  static const Color placeholder = Color(0xFF64748B);       // #64748B

  // Security Status Semantics (Distinct & Semantic)
  static const Color safe = Color(0xFF22C55E);              // #22C55E - SAFE
  static const Color safeBg = Color(0x1F22C55E);            // Subtle Dark Green Tint (12%)
  
  static const Color suspicious = Color(0xFFF59E0B);        // #F59E0B - SUSPICIOUS
  static const Color suspiciousBg = Color(0x1FF59E0B);      // Subtle Dark Amber Tint (12%)
  
  static const Color malicious = Color(0xFFEF4444);         // #EF4444 - MALICIOUS
  static const Color maliciousBg = Color(0x1FEF4444);       // Subtle Dark Red Tint (12%)

  static const Color block = Color(0xFFDC2626);             // #DC2626 - BLOCKED
  static const Color blockBg = Color(0x1FDC2626);           // Subtle Dark Block Tint (12%)
}

class AppTheme {
  // Aliases mapping to QRadarColors for backward compatibility and clean referencing
  static const Color background = QRadarColors.primaryBackground;
  static const Color deepNavy = QRadarColors.deepNavy;
  static const Color sidebar = QRadarColors.sidebar;
  static const Color surface = QRadarColors.surface;
  static const Color surfaceElevated = QRadarColors.surfaceElevated;
  static const Color border = QRadarColors.border;
  static const Color borderLight = QRadarColors.borderLight;

  static const Color primary = QRadarColors.primaryBlue;
  static const Color primaryBlue = QRadarColors.primaryBlue;
  static const Color secondaryBlue = QRadarColors.secondaryBlue;
  static const Color primaryGradientEnd = QRadarColors.secondaryBlue;
  static const Color accent = QRadarColors.accentCyan;
  static const Color accentCyan = QRadarColors.accentCyan;

  static const Color textPrimary = QRadarColors.textPrimary;
  static const Color textSecondary = QRadarColors.textSecondary;
  static const Color textSubtle = QRadarColors.textSubtle;
  static const Color textMuted = QRadarColors.textMuted;

  static const Color safe = QRadarColors.safe;
  static const Color safeBg = QRadarColors.safeBg;
  
  static const Color suspicious = QRadarColors.suspicious;
  static const Color suspiciousBg = QRadarColors.suspiciousBg;
  
  static const Color malicious = QRadarColors.malicious;
  static const Color maliciousBg = QRadarColors.maliciousBg;

  static const Color block = QRadarColors.block;
  static const Color blockBg = QRadarColors.blockBg;

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: QRadarColors.primaryBackground,
      primaryColor: QRadarColors.primaryBlue,
      canvasColor: QRadarColors.primaryBackground,
      colorScheme: const ColorScheme.dark(
        primary: QRadarColors.primaryBlue,
        secondary: QRadarColors.accentCyan,
        surface: QRadarColors.surface,
        error: QRadarColors.malicious,
        onPrimary: QRadarColors.primaryBackground,
        onSurface: QRadarColors.textPrimary,
        onSurfaceVariant: QRadarColors.textSecondary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: QRadarColors.surface,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: QRadarColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.3,
        ),
        iconTheme: IconThemeData(color: QRadarColors.textPrimary),
      ),
      cardTheme: CardTheme(
        color: QRadarColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: QRadarColors.border, width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: QRadarColors.primaryBlue,
          foregroundColor: QRadarColors.primaryBackground,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 15),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.4,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          backgroundColor: QRadarColors.surfaceElevated,
          foregroundColor: QRadarColors.textPrimary,
          side: const BorderSide(color: QRadarColors.border, width: 1.2),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: QRadarColors.surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: QRadarColors.border, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: QRadarColors.border, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: QRadarColors.primaryBlue, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: QRadarColors.malicious, width: 1.5),
        ),
        hintStyle: const TextStyle(color: QRadarColors.placeholder, fontSize: 13),
        labelStyle: const TextStyle(color: QRadarColors.textSecondary, fontSize: 13),
      ),
      dividerTheme: const DividerThemeData(
        color: QRadarColors.border,
        thickness: 1,
        space: 1,
      ),
    );
  }

  static Color getVerdictColor(String verdict) {
    switch (verdict.toUpperCase()) {
      case 'SAFE':
        return QRadarColors.safe;
      case 'SUSPICIOUS':
        return QRadarColors.suspicious;
      case 'MALICIOUS':
        return QRadarColors.malicious;
      case 'BLOCK':
      case 'BLOCKED':
        return QRadarColors.block;
      default:
        return QRadarColors.textSecondary;
    }
  }

  static Color getVerdictBgColor(String verdict) {
    switch (verdict.toUpperCase()) {
      case 'SAFE':
        return QRadarColors.safeBg;
      case 'SUSPICIOUS':
        return QRadarColors.suspiciousBg;
      case 'MALICIOUS':
        return QRadarColors.maliciousBg;
      case 'BLOCK':
      case 'BLOCKED':
        return QRadarColors.blockBg;
      default:
        return QRadarColors.surfaceElevated;
    }
  }

  static Color getScoreColor(int score) {
    if (score < 30) return QRadarColors.safe;
    if (score < 70) return QRadarColors.suspicious;
    return QRadarColors.malicious;
  }
}
