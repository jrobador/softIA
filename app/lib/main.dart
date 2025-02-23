// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/chatbot_provider.dart';
import 'screens/chatbot_lists_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatbotProvider()),
      ],
      child: GPTManagerApp(),
    ),
  );
}

class GPTManagerApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tu lista de asistentes virtuales',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: ChatbotListScreen(),
    );
  }
}
