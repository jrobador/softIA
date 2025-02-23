// lib/screens/chatbot_chat_screen.dart
// chatgpt no sabe que pliegos usa ecogas
import 'package:flutter/material.dart';
import '../models/chatbot.dart';
import '../widgets/chat_message.dart';

class ChatbotChatScreen extends StatefulWidget {
  final Chatbot chatbot;

  ChatbotChatScreen({required this.chatbot});

  @override
  _ChatbotChatScreenState createState() => _ChatbotChatScreenState();
}

class _ChatbotChatScreenState extends State<ChatbotChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isSending = false;

  // Simulated response
  final String simulatedResponse = """
Tras analizar los pliegos técnicos proporcionados por la empresa, se identificaron los siguientes requisitos clave para los transmisores de presión diferencial:

- Rango de medición: 0-600 mbar (según especificación en el ítem 4.2 del pliego EC-GAS-2023).
- Certificación: SIL 2 para seguridad funcional (exigido en el apartado 7.1.3).
- Protocolo de comunicación: HART/Profibus-PA (requerido en la sección 5.4).
- Ambiente: Resistencia a temperaturas entre -40°C y 85°C (cláusula 3.7).

Cantidad requerida:
Según los puntos de medición detallados en los diagramas P&ID (Anexo D), se necesitan 4 transmisores de presión diferencial.

Marca y modelo recomendado:
El Siemens Sitrans P320 (disponible en inventario, código INV-TR-0452) cumple con todos los requisitos:

- Rango ajustable: 0-1000 mbar (supera lo solicitado).
- Certificaciones: SIL 2, ATEX, y IP67 (adecuado para áreas clasificadas).
- Integración: Compatibilidad nativa con Profibus-PA y HART.
- Ambiente: Opera en -50°C a 100°C, ideal para las condiciones extremas del proyecto EC-GAS.

Alternativas en inventario:
Emerson Rosemount 3051S (INV-TR-0781): Cumple parcialmente, pero no incluye SIL 2. """;
  final int responseDelay = 3; // Delay in seconds

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
      _isSending = true;
    });

    _controller.clear();

    try {
      // Simulate API delay
      await Future.delayed(Duration(seconds: responseDelay));

      setState(() {
        _messages.add(ChatMessage(text: simulatedResponse, isUser: false));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(text: 'Error: ${e.toString()}', isUser: false));
      });
    } finally {
      setState(() {
        _isSending = false;
      });
    }
  }

  Widget _buildMessageList() {
    return ListView.builder(
      reverse: true,
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        ChatMessage message = _messages[_messages.length - 1 - index];
        return ChatMessageWidget(message: message);
      },
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8.0),
      color: Colors.white,
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Escribe tu mensaje...',
                border: InputBorder.none,
              ),
              onSubmitted: _isSending ? null : _sendMessage,
            ),
          ),
          IconButton(
            icon: _isSending 
              ? SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2)
                ) 
              : Icon(Icons.send),
            onPressed: _isSending ? null : () => _sendMessage(_controller.text),
            color: Colors.blue,
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Consulta de materiales"),
        backgroundColor: Colors.blue,
      ),
      body: Column(
        children: [
          Expanded(child: _buildMessageList()),
          Divider(height: 1.0),
          _buildInputArea(),
        ],
      ),
    );
  }
}