import { useRef, useEffect, useCallback } from 'react';
import { MOUSE_THROTTLE_MS } from '../config';

/**
 * Canvas hook — handles frame rendering, mouse capture, and keyboard capture.
 */
export function useRemoteCanvas({ hostScreen, lastFrame, lastDelta, send }) {
  const canvasRef = useRef(null);
  const lastMouseSendRef = useRef(0);

  // ---------- Frame rendering ----------

  const drawFullFrame = useCallback(
    async (frame) => {
      const canvas = canvasRef.current;
      if (!canvas || !frame?.data) return;
      const ctx = canvas.getContext('2d');

      try {
        const bytes = Uint8Array.from(atob(frame.data), (c) => c.charCodeAt(0));
        const blob = new Blob([bytes], { type: 'image/jpeg' });
        const bmp = await createImageBitmap(blob);

        canvas.width = frame.width || bmp.width;
        canvas.height = frame.height || bmp.height;
        ctx.drawImage(bmp, 0, 0);
        bmp.close();
      } catch (e) {
        console.error('Frame render error:', e);
      }
    },
    []
  );

  const drawDeltaFrame = useCallback(
    async (delta) => {
      const canvas = canvasRef.current;
      if (!canvas || !delta?.regions?.length) return;
      const ctx = canvas.getContext('2d');

      for (const region of delta.regions) {
        try {
          const bytes = Uint8Array.from(atob(region.data), (c) =>
            c.charCodeAt(0)
          );
          const blob = new Blob([bytes], { type: 'image/jpeg' });
          const bmp = await createImageBitmap(blob);
          ctx.drawImage(bmp, region.x, region.y, region.width, region.height);
          bmp.close();
        } catch (e) {
          console.error('Delta region render error:', e);
        }
      }
    },
    []
  );

  useEffect(() => {
    if (lastFrame) drawFullFrame(lastFrame);
  }, [lastFrame, drawFullFrame]);

  useEffect(() => {
    if (lastDelta) drawDeltaFrame(lastDelta);
  }, [lastDelta, drawDeltaFrame]);

  // ---------- Coordinate helpers ----------

  const canvasToRelative = useCallback(
    (e) => {
      const canvas = canvasRef.current;
      if (!canvas || !hostScreen) return null;

      const rect = canvas.getBoundingClientRect();
      // Map display position to host screen coords (0-1)
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      return {
        x: Math.max(0, Math.min(1, x)),
        y: Math.max(0, Math.min(1, y)),
      };
    },
    [hostScreen]
  );

  // ---------- Mouse handlers ----------

  const handleMouseMove = useCallback(
    (e) => {
      const now = Date.now();
      if (now - lastMouseSendRef.current < MOUSE_THROTTLE_MS) return;
      lastMouseSendRef.current = now;

      const pos = canvasToRelative(e);
      if (!pos) return;
      send({ type: 'mouse_move', x: pos.x, y: pos.y });
    },
    [canvasToRelative, send]
  );

  const buttonName = (btn) => {
    if (btn === 2) return 'right';
    if (btn === 1) return 'middle';
    return 'left';
  };

  const handleMouseDown = useCallback(
    (e) => {
      const pos = canvasToRelative(e);
      if (!pos) return;
      send({
        type: 'mouse_click',
        x: pos.x,
        y: pos.y,
        button: buttonName(e.button),
        action: 'down',
      });
    },
    [canvasToRelative, send]
  );

  const handleMouseUp = useCallback(
    (e) => {
      const pos = canvasToRelative(e);
      if (!pos) return;
      send({
        type: 'mouse_click',
        x: pos.x,
        y: pos.y,
        button: buttonName(e.button),
        action: 'up',
      });
    },
    [canvasToRelative, send]
  );

  const handleClick = useCallback(
    (e) => {
      const pos = canvasToRelative(e);
      if (!pos) return;
      send({
        type: 'mouse_click',
        x: pos.x,
        y: pos.y,
        button: buttonName(e.button),
        action: 'click',
      });
    },
    [canvasToRelative, send]
  );

  const handleDoubleClick = useCallback(
    (e) => {
      const pos = canvasToRelative(e);
      if (!pos) return;
      send({
        type: 'mouse_click',
        x: pos.x,
        y: pos.y,
        button: buttonName(e.button),
        action: 'dblclick',
      });
    },
    [canvasToRelative, send]
  );

  const handleWheel = useCallback(
    (e) => {
      e.preventDefault();
      const pos = canvasToRelative(e);
      if (!pos) return;
      const delta = Math.sign(e.deltaY) * Math.min(Math.abs(e.deltaY), 10);
      send({ type: 'mouse_scroll', x: pos.x, y: pos.y, delta });
    },
    [canvasToRelative, send]
  );

  const handleContextMenu = useCallback((e) => {
    e.preventDefault();
  }, []);

  // ---------- Keyboard capture ----------

  useEffect(() => {
    const MODIFIER_KEYS = new Set([
      'Control',
      'Shift',
      'Alt',
      'Meta',
    ]);

    const mapKey = (key) => {
      const map = {
        Control: 'ctrl',
        Shift: 'shift',
        Alt: 'alt',
        Meta: 'meta',
        Enter: 'enter',
        Backspace: 'backspace',
        Tab: 'tab',
        Escape: 'escape',
        ArrowUp: 'up',
        ArrowDown: 'down',
        ArrowLeft: 'left',
        ArrowRight: 'right',
        Delete: 'delete',
        Home: 'home',
        End: 'end',
        PageUp: 'pageup',
        PageDown: 'pagedown',
        ' ': 'space',
      };
      return map[key] || key.toLowerCase();
    };

    const handleKeyDown = (e) => {
      // Build active modifiers
      const mods = [];
      if (e.ctrlKey) mods.push('ctrl');
      if (e.altKey) mods.push('alt');
      if (e.shiftKey) mods.push('shift');
      if (e.metaKey) mods.push('meta');

      const key = mapKey(e.key);

      // If this is a modifier-only press, just send key_event
      if (MODIFIER_KEYS.has(e.key)) {
        send({ type: 'key_event', key, action: 'down' });
        e.preventDefault();
        return;
      }

      // Combo: modifier(s) + non-modifier key
      if (mods.length > 0) {
        const comboKeys = [...new Set([...mods, key])];
        send({ type: 'key_combo', keys: comboKeys });
        e.preventDefault();
        return;
      }

      // Regular key press
      send({ type: 'key_event', key, action: 'press' });
      e.preventDefault();
    };

    const handleKeyUp = (e) => {
      if (MODIFIER_KEYS.has(e.key)) {
        send({ type: 'key_event', key: mapKey(e.key), action: 'up' });
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [send]);

  return {
    canvasRef,
    mouseHandlers: {
      onMouseMove: handleMouseMove,
      onMouseDown: handleMouseDown,
      onMouseUp: handleMouseUp,
      onClick: handleClick,
      onDoubleClick: handleDoubleClick,
      onWheel: handleWheel,
      onContextMenu: handleContextMenu,
    },
  };
}
