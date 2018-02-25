package org.cs231a.ptam;

public class HelloWorld {
  public void sayHello(MessageProcessor processor) {
    System.out.println(processor.processMessage("Hello"));
  }

  public static interface MessageProcessor {
    String processMessage(String message);
  }
}
