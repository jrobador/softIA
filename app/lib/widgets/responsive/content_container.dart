import 'package:flutter/material.dart';
import '../../config/breakpoints.dart';
import '../../utils/responsive_utils.dart';

class ContentContainer extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;

  const ContentContainer({
    Key? key,
    required this.child,
    this.padding,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: Breakpoints.maxContentWidth,
        ),
        child: Padding(
          padding: padding ?? ResponsiveUtils.getResponsivePadding(context),
          child: child,
        ),
      ),
    );
  }
}