package org.cs231a.ptam;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.Rect;
import android.widget.LinearLayout;


public class AugmentationLinearLayout extends LinearLayout {

    private int rectLeft = 0;
    private int rectTop = 10;
    private int rectRight = 200;
    private int rectBottom = 300;

    public AugmentationLinearLayout(Context context) {
      super(context);

      setWillNotDraw(false);
    }

    @Override
    public void draw(Canvas canvas) {
      super.draw(canvas);

      Paint paint = new Paint();
      paint.setColor(Color.GREEN);
      Rect rect = new Rect(rectLeft, rectTop, rectRight, rectBottom);
      canvas.drawRect(rect, paint);
    }

    public void setRectCoordinates(int rectLeft, int rectTop, int rectRight, int rectBottom) {
      this.rectLeft = rectLeft;
      this.rectTop = rectTop;
      this.rectRight = rectRight;
      this.rectBottom = rectBottom;
    }
}
