import 'package:flutter/material.dart';
import '../config/breakpoints.dart';

class ResponsiveUtils {
  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < Breakpoints.tablet;
      
  static bool isTablet(BuildContext context) =>
      MediaQuery.of(context).size.width >= Breakpoints.tablet &&
      MediaQuery.of(context).size.width < Breakpoints.desktop;
      
  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= Breakpoints.desktop;
      
  static double getContentMaxWidth(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width > Breakpoints.maxContentWidth ? Breakpoints.maxContentWidth : width;
  }
  
  static EdgeInsets getResponsivePadding(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.all(16.0);
    } else if (isTablet(context)) {
      return const EdgeInsets.all(24.0);
    }
    return const EdgeInsets.all(32.0);
  }
  
  static double getResponsiveSpacing(BuildContext context) {
    if (isMobile(context)) return 16.0;
    if (isTablet(context)) return 24.0;
    return 32.0;
  }
}