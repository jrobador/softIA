import 'package:flutter/material.dart';
import '../../utils/responsive_utils.dart';

class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayout({
    Key? key,
    required this.mobile,
    this.tablet,
    this.desktop,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (ResponsiveUtils.isDesktop(context)) {
          return desktop ?? tablet ?? mobile;
        }
        if (ResponsiveUtils.isTablet(context)) {
          return tablet ?? mobile;
        }
        return mobile;
      },
    );
  }
}