// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/chatbot_provider.dart';
import 'screens/chatbot_lists_screen.dart';
import 'config/theme.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatbotProvider()),
      ],
      child: const GPTManagerApp(),
    ),
  );
}

class GPTManagerApp extends StatelessWidget {
  const GPTManagerApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SoftIA',
      theme: AppTheme.lightTheme,
      home: ChatbotListScreen(),
    );
  }
}