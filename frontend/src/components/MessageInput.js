import { Ionicons } from '@expo/vector-icons';
import { useState } from 'react';
import { Platform, Pressable, StyleSheet, TextInput, View } from 'react-native';

export default function MessageInput({ disabled, onSend }) {
  const [value, setValue] = useState('');

  function handleSend() {
    const text = value.trim();
    if (!text || disabled) return;

    setValue('');
    onSend(text);
  }

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={setValue}
        placeholder="Ask MediBot..."
        placeholderTextColor="#64748b"
        editable={!disabled}
        multiline
        onKeyPress={(event) => {
          const { nativeEvent } = event;
          if (Platform.OS === 'web' && nativeEvent.key === 'Enter' && !nativeEvent.shiftKey) {
            event.preventDefault?.();
            handleSend();
          }
        }}
      />
      <Pressable
        accessibilityLabel="Send message"
        disabled={disabled || !value.trim()}
        onPress={handleSend}
        style={({ pressed }) => [
          styles.button,
          (disabled || !value.trim()) && styles.buttonDisabled,
          pressed && styles.buttonPressed,
        ]}
      >
        <Ionicons name="send" color="#ffffff" size={18} />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
    borderTopColor: '#e2e8f0',
    borderTopWidth: 1,
    backgroundColor: '#ffffff',
    padding: 16,
  },
  input: {
    flex: 1,
    maxHeight: 140,
    minHeight: 50,
    borderColor: '#cbd5e1',
    borderRadius: 8,
    borderWidth: 1,
    color: '#0f172a',
    fontSize: 16,
    paddingHorizontal: 16,
    paddingVertical: 13,
  },
  button: {
    alignItems: 'center',
    backgroundColor: '#0891b2',
    borderRadius: 8,
    height: 50,
    justifyContent: 'center',
    width: 50,
  },
  buttonDisabled: {
    backgroundColor: '#94a3b8',
  },
  buttonPressed: {
    opacity: 0.85,
  },
});
