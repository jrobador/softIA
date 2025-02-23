// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/chatbot_provider.dart';
import 'screens/chatbot_lists_screen.dart';
import 'models/chatbot.dart';
import 'package:uuid/uuid.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) {
          ChatbotProvider provider = ChatbotProvider();
          provider.addChatbot(Chatbot(
            id: Uuid().v4(),
            name: 'Consulta de materiales',
            useCase: 'Estimador de materiales para nuevos proyectos',
            filePaths: [],
            isLocal: true
          ));
          return provider;
        }),
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
