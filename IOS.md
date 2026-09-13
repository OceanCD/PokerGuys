# PokerGuys on iOS

PokerGuys now has two iPhone delivery paths that share the same HTML, CSS, and JavaScript.

## 1. Install from Safari (ready now)

The deployed site is a Progressive Web App. On an iPhone:

1. Open the production URL in Safari.
2. Tap **Share**.
3. Tap **Add to Home Screen**.
4. Launch PokerGuys from its new Home Screen icon.

It opens in a standalone window, respects the iPhone safe areas, caches the application shell, and keeps an in-progress table in local storage.

## 2. Build the App Store version with Capacitor

The native wrapper is configured with the bundle identifier `com.oceancd.pokerguys`. Change that identifier in `capacitor.config.json` before the first App Store release if it does not match the Apple Developer account.

Prerequisites:

- Node.js and npm
- The full Xcode app (Command Line Tools alone are not enough)
- An Apple Developer account for device/TestFlight/App Store distribution

Commands:

```bash
npm install
npm run ios:sync    # after every web UI change
npm run ios:open
```

The `ios/` Xcode project is already generated and committed. Use `npm run ios:add` only if that directory is deliberately removed and needs to be recreated.

In Xcode, select the `App` target, choose the development team, confirm the bundle identifier, and run on a simulator or connected iPhone. Use **Product → Archive** when the build is ready for TestFlight.

## Release checklist

- Replace the current community-code-only access model with real Supabase Auth and member-based Row Level Security before storing private group data.
- Supply a working review community or a built-in demo mode for App Review.
- Remove or finish any visible placeholder features before submission.
- Add a privacy policy and App Store privacy answers for data synced through Supabase.
- Test offline launch, session restore, keyboard behavior, safe areas, VoiceOver labels, and both English and Chinese on a physical iPhone.
- Add at least one useful native capability (haptics are wired into this project; sharing or notifications are natural next steps) so the App Store build clearly feels more capable than a web clipping.

The repository currently has Apple Command Line Tools but not the full Xcode app, so signing, simulator testing, and archiving must be completed after Xcode is installed.
