We are given a merge conflict in CHANGELOG.md between base (master) and head (fix/git-log-tformat-9860470550172230739).
 We have the ancestor, base, and head versions.

 Steps:
 1. We note that the base (master) has added versions [1.0.22] and [1.0.21] (and others) and the head has added [1.0.21] and [1.0.20].
 2. The conflict is in the top part of the file (the changelog entries).

 However, note that the base and head both have changes that are not overlapping in the same lines? Actually, the base has:
   [1.0.22] and then [1.0.21] (which is the same as the head's [1.0.21] but with a different change?).

 Let's look at the provided diff (Head changes vs base) which shows:

   @@ -1,5 +1,15 @@
    # Changelog
 
   +## [1.0.21] - 2026-05-21
   +
   +### Changed
   +* **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.
   +
   +## [1.0.20] - 2026-05-20
   +
   +### Changed
   +* **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.
   
    ## [1.0.19] - 2026-05-06
 
    ### Changed

 This diff indicates that the base (master) had at the top:
    ## [1.0.22] - 2026-05-22
    ... (then the rest)

 But the head (PR branch) has:
    ## [1.0.21] - 2026-05-21
    ... (then the rest) and then also added [1.0.20] above the existing [1.0.19].

 However, note that the base (master) already had [1.0.21] and [1.0.20] in its history? Actually, from the base version we see:

   Base (master) has:
      ## [1.0.22] - 2026-05-22
      ## [1.0.21] - 2026-05-21
      ... and so on.

 But the head (PR branch) has:
      ## [1.0.21] - 2026-05-21
      ## [1.0.20] - 2026-05-20
      ... and then the rest.

 The conflict arises because the base has a [1.0.22] that the head does not have, and the head has a [1.0.20] that the base does not have at the same position? Actually, the base has [1.0.21] and [1.0.20] in its history but they are not at the top? Let me clarify:

 The base (master) version provided in the file versions section shows:

   Base (master):
      ## [1.0.22] - 2026-05-22
      ## [1.0.21] - 2026-05-21
      ... (then older versions)

 The head (PR branch) version shows:
      ## [1.0.21] - 2026-05-21
      ## [1.0.20] - 2026-05-20
      ... (then older versions)

 But note: the base (master) also has [1.0.20] and [1.0.19] etc. in its history, but they are not shown in the truncated version? Actually, the base version provided in the file versions section is truncated.

 However, the diff (Head changes vs base) shows that the base had at the top (before the head changes) the line "## [1.0.19] - 2026-05-06", meaning that the base version we are comparing against in the diff is actually the version that had [1.0.19] at the top? But wait, the base (master) we are given in the file versions section has [1.0.22] at the top.

 This is confusing. Let me re-read the context:

   Base (master): 93 lines changed (lines 3-116)
        ... shows base has [1.0.22] and then [1.0.21] etc.

   Head: 85 lines changed (lines 3-111)
        ... shows head has [1.0.21] and then [1.0.20] etc.

 And the diff (Head changes vs base) shows:

   @@ -1,5 +1,15 @@
    # Changelog
 
   +## [1.0.21] - 2026-05-21
   + ... 
   +## [1.0.20] - 2026-05-20
   + ...
    ## [1.0.19] - 2026-05-06

 This implies that the base version (against which the head diff is taken) had at the top:

    # Changelog
    ## [1.0.19] - 2026-05-06

 But wait, the base (master) we are given in the file versions section has [1.0.22] at the top. This suggests that the base (master) has moved forward and the head branch is based on an older version of master? Actually, the ancestor is the common base.

 How to resolve:

 We are told:
   - Base (master) is the target branch (has newer changes from others)
   - Head branch is the PR branch (has the PR author's changes)

 So the base (master) is the branch we are merging into, and the head is the feature branch.

 The merge base (ancestor) is the point from which both diverged.

 We are to keep all meaningful changes from both branches.

 Steps for resolution:

 1. We note that the base (master) has added a new version [1.0.22] at the top, and also modified the [1.0.21] entry (with a reliability fix about CODEDNA_MAX_FILE_SIZE) and then has the rest of the changelog.

 2. The head branch has added a new version [1.0.21] (which is the same version as in base but with a different change: fixing git log crashes by using tformat:) and then added [1.0.20] (with a testing fix) and then the rest.

 However, note that the base (master) already has a [1.0.21] entry (with a different change: wrapping CODEDNA_MAX_FILE_SIZE in try-except). The head branch also has a [1.0.21] entry (with the tformat: fix).

 This is a conflict in the same version section? Actually, no: the base has [1.0.22] and then [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix) and the head has [1.0.21] (with the tformat: fix) and then [1.0.20].

 But wait: the base (master) does not have [1.0.20] at the top? It has [1.0.22] and then [1.0.21] and then the rest (which includes [1.0.20] and older). Similarly, the head branch has [1.0.21] and [1.0.20] and then the rest (which includes [1.0.19] and older).

 However, the diff shows that the base (against which the head diff is taken) had [1.0.19] at the top? This suggests that the head branch was branched off from an older version of master (before [1.0.20] and [1.0.21] and [1.0.22] were added).

 Therefore, when merging, we want to:

   - Keep the base's [1.0.22] (since it's new in base and not in head)
   - Then, we have two different [1.0.21] entries: one from base (with CODEDNA_MAX_FILE_SIZE fix) and one from head (with tformat: fix). We must combine them? But note: they are two different changes to the same version? Actually, no: they are two different commits that both claim to be version 1.0.21? That doesn't make sense.

 Let me look at the actual changes:

   Base (master) for [1.0.21]:
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

   Head branch for [1.0.21]:
        * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

 These are two different changes. They are both reliability fixes but for different issues.

 Since they are in the same version section, we cannot have two separate entries for the same version. We must merge the changes under the same version.

 However, note: the base (master) has [1.0.22] and then [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix) and then the head branch has [1.0.21] (with the tformat: fix) and then [1.0.20]. But wait, the base (master) also has [1.0.20] in its history? Yes, because the base (master) has [1.0.22], [1.0.21], [1.0.20], ... etc.

 The head branch, however, does not have [1.0.22] and has [1.0.21] and [1.0.20] and then the rest.

 How should we merge?

   We want to include:
      - The base's [1.0.22] (because it's new in base and not in head)
      - Then, for [1.0.21]: we have two sets of changes. We should combine them? But note: the base's [1.0.21] and the head's [1.0.21] are two different commits that both modified the same version? Actually, no: the head branch does not have the base's [1.0.22] and so when the head branch was created, the base only had up to [1.0.19] (or so). Then the head branch added [1.0.21] and [1.0.20] (which are actually newer than [1.0.19] but older than [1.0.22]?).

   This is confusing because the version numbers are not in order? Actually, the version numbers should be increasing. The base has [1.0.22] as the latest, then [1.0.21], then [1.0.20], etc. The head branch has [1.0.21] as the latest (in the head branch) and then [1.0.20], etc.

   But note: the head branch's [1.0.21] is actually an older version than the base's [1.0.22]? And the head branch's [1.0.20] is older than the base's [1.0.21]? So when we merge, we want:

        [1.0.22] (from base)
        [1.0.21] (we have two changes: one from base and one from head? But wait, the base's [1.0.21] is already in the base and the head branch also has a [1.0.21] that is different? Actually, the head branch's [1.0.21] is a different change that was made independently.)

   However, the version number 1.0.21 cannot have two different sets of changes. We must decide: which one is correct?

   But note: the base (master) is the target branch and has the [1.0.22] and [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix). The head branch (PR) is trying to add [1.0.21] and [1.0.20] on top of an older base.

   The correct approach is to rebase the head branch onto the latest base? But we are doing a merge.

   Since we are told to keep all meaningful changes from both branches, we must:

        - Keep the base's [1.0.22] (because it's new in base)
        - Then, we have the base's [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix) and the head's [1.0.21] (with the tformat: fix). We should combine the changes for version 1.0.21? But note: the head branch also has a [1.0.20] that the base does not have at that position? Actually, the base does have [1.0.20] but it is after [1.0.21] (in the base, the order is [1.0.22], [1.0.21], [1.0.20], ...). The head branch has [1.0.21] and then [1.0.20] (so the same order as base for these two).

   However, the head branch's [1.0.20] is actually the same as the base's [1.0.20]? Let's check:

        Base (master) for [1.0.20]:
            ## [1.0.20] - 2026-05-20
            ### Changed
            * **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.

        Head branch for [1.0.20]:
            ## [1.0.20] - 2026-05-20
            ### Changed
            * **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.

   They are identical.

   Similarly, the base (master) for [1.0.19] and the head branch for [1.0.19] are the same? We don't have the full text, but from the context it seems they are the same.

   Therefore, the only differences are:

        Base has:
            [1.0.22] (new)
            [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix)

        Head has:
            [1.0.21] (with the tformat: fix)   [but note: this is the same version number as base's [1.0.21] but a different change]
            [1.0.20] (which base also has, but base has it after [1.0.21])

   However, the head branch does not have the base's [1.0.22] and has its own [1.0.21] (which is actually a different change) and then [1.0.20].

   How to resolve the version 1.0.21 conflict?

   We have two different changes for the same version. We must combine them? But note: the version number must be unique. We cannot have two different [1.0.21] sections.

   Since the base (master) is the target branch and already released [1.0.22] (which includes [1.0.21] with the CODEDNA_MAX_FILE_SIZE fix), and the head branch is trying to introduce a [1.0.21] with a different fix, we must consider:

        The head branch's [1.0.21] change (tformat: fix) is actually more recent than the base's [1.0.21]? Or is it?

   Looking at the dates:

        Base's [1.0.21]: 2026-05-21
        Head's [1.0.21]: 2026-05-21   (same date)

   But the base's [1.0.22] is 2026-05-22, which is after.

   The head branch's [1.0.20] is 2026-05-20.

   So the timeline:

        2026-05-20: [1.0.20] (both base and head have this, but base has it as the third version and head as the second)
        2026-05-21: 
             base: [1.0.21] (with CODEDNA_MAX_FILE_SIZE fix) and then [1.0.22] (next day)
             head: [1.0.21] (with tformat: fix)   [and then they have [1.0.20] which is actually older?]

   This doesn't make sense because the head branch has [1.0.21] and then [1.0.20] (which is out of order).

   I suspect that the head branch's changelog entries are in reverse chronological order? Actually, changelogs are usually in reverse chronological order (newest first). So:

        Base (master):
            [1.0.22] - 2026-05-22   (newest)
            [1.0.21] - 2026-05-21
            [1.0.20] - 2026-05-20
            ... 

        Head branch:
            [1.0.21] - 2026-05-21   (newest in the head branch)
            [1.0.20] - 2026-05-20
            [1.0.19] - 2026-05-06
            ...

   But wait, the head branch does not have [1.0.22]? So when we merge, we want to put the base's [1.0.22] at the top, then we have to decide what to do with [1.0.21].

   The base's [1.0.21] and the head's [1.0.21] are two different changes that were made independently on the same base version (the version before 1.0.21). We should combine the changes for version 1.0.21.

   However, note: the base's [1.0.21] change (CODEDNA_MAX_FILE_SIZE) and the head's [1.0.21] change (tformat:) are two separate commits that both modified the same codebase? They are in different files? We don't have the code, but from the description they are in different parts:

        Base's [1.0.21]: 
            * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        Head's [1.0.21]:
            * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

   They are two different reliability fixes. We can combine them by having both bullet points under the same version.

   Therefore, for version [1.0.21] we should have:

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.
        * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

   But note: the base's [1.0.21] already has one bullet and the head's [1.0.21] has one bullet. We can put both.

   However, we must be cautious: the base's [1.0.21] might have more than one bullet? We don't have the full text, but from the diff we see only one.

   Similarly, the head's [1.0.21] has only one bullet.

   Now, what about the [1.0.20]? The base has [1.0.20] and the head has [1.0.20] and they are identical? We can keep one.

   And the base has [1.0.22] which the head does not have.

   So the merged changelog should be:

        # Changelog

        ## [1.0.22] - 2026-05-22

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        ## [1.0.21] - 2026-05-21

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.
        * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

        ## [1.0.20] - 2026-05-20

        ### Changed
        * **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.

        ... and then the rest (from [1.0.19] onwards) which is the same in both.

   But wait: the base's [1.0.21] already had the first bullet, and we are adding the second bullet from the head. However, note that the head's [1.0.21] also says "Pruned zero files." and the base's [1.0.21] also says that. We are duplicating the "Pruned zero files."? 

   Actually, the two changes are independent and both pruned zero files? It's possible that they are two separate pruning operations. But to avoid duplication, we might want to combine the notes? However, the instructions say to keep all meaningful changes. Since they are two separate changes, we keep both bullets.

   Alternatively, we could note that the "Pruned zero files." is redundant and only mention it once? But we don't know if they are the same pruning. Since we are not sure, and to be safe, we keep both.

   However, let me check the base's [1.0.21] and head's [1.0.21] in the provided file versions:

        Base (master) for [1.0.21]:
            * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        Head branch for [1.0.21]:
            * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

   They are two different sentences. We can keep both.

   But note: the base (master) also has a [1.0.22] that says "Pruned zero files."? Let me check:

        Base (master) for [1.0.22]:
            * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

   So the base's [1.0.22] and [1.0.21] both have "Pruned zero files."? That seems odd. It might be a mistake, but we are not to change the meaning.

   We are only to resolve the merge conflict by keeping changes from both branches.

   Therefore, we will output:

        # Changelog

        ## [1.0.22] - 2026-05-22

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        ## [1.0.21] - 2026-05-21

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.
        * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

        ## [1.0.20] - 2026-05-20

        ### Changed
        * **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.

        ... and then the rest of the changelog from [1.0.19] onwards (which is the same in both branches).

   However, note: the base (master) has more than just [1.0.22], [1.0.21], [1.0.20]? It has older versions. Similarly, the head branch has older versions. We must include the entire changelog.

   But the base (master) and head branch both have the same older versions (from [1.0.19] downwards) because the head branch was branched off from an older base and then the base added [1.0.20], [1.0.21], [1.0.22] on top? Actually, no: the base has [1.0.22] at the top and then [1.0.21] and then [1.0.20] and then the rest. The head branch has [1.0.21] and then [1.0.20] and then the rest. So the rest (from [1.0.19] down) is the same.

   Therefore, we can take the base's changelog from [1.0.22] down to [1.0.20] (which we are going to modify for [1.0.21]) and then append the rest from the base (or head, since they are the same) starting from [1.0.19].

   However, note: the base's [1.0.20] is the same as the head's [1.0.20]? We assume so.

   But wait: the base (master) might have changed [1.0.20] after the head branch was branched? We don't have that information. However, the diff (Head changes vs base) shows that the base had [1.0.19] at the top of the diff section? Actually, the diff shows:

        @@ -1,5 +1,15 @@
         # Changelog
 
        +## [1.0.21] - 2026-05-21
        + ...
        +## [1.0.20] - 2026-05-20
        + ...
         ## [1.0.19] - 2026-05-06

   This means that the base (against which the head diff is taken) had at the top:

        # Changelog
        ## [1.0.19] - 2026-05-06

   and then the rest. But the base (master) we are given in the file versions section has [1.0.22] at the top. This indicates that the base (master) has moved forward and the diff we are looking at is not against the very latest base? 

   Actually, the diff (Head changes vs base) is showing the changes that the head branch has made relative to the base branch at the time of the merge base? Or is it showing the changes that the head branch has made relative to the base branch (which is the target) but the target has moved forward?

   In a 3-way merge, we have:

        ancestor: common base
        base: the target branch (master) at the time of merge
        head: the feature branch

   The diff (Head changes vs base) is actually showing the difference between the head branch and the base branch? But note: the base branch in the diff is the target branch (master) and the head branch is the feature branch.

   However, the diff output we are given is:

        @@ -1,5 +1,15 @@
         # Changelog
 
        +## [1.0.21] - 2026-05-21
        + ...
        +## [1.0.20] - 2026-05-20
        + ...
         ## [1.0.19] - 2026-05-06

   This means that the base branch (master) at the time of the diff had:

        # Changelog
        ## [1.0.19] - 2026-05-06
        ... (and then the rest)

   and the head branch has:

        # Changelog
        ## [1.0.21] - 2026-05-21
        ... 
        ## [1.0.20] - 2026-05-20
        ...
        ## [1.0.19] - 2026-05-06
        ... (same as base)

   But wait, that would mean the head branch has added two new versions on top of the base? However, the base (master) we are given in the file versions section has [1.0.22] and [1.0.21] and [1.0.20] and then [1.0.19] etc. This suggests that the base (master) has progressed beyond the point where the head branch was branched.

   Therefore, when we merge, we want to take the base (master) as the starting point and then incorporate the head branch's changes that are not in the base.

   The head branch has:

        [1.0.21] (with the tformat: fix) and [1.0.20] (with the testing fix) 

   but the base (master) already has:

        [1.0.22] (new)
        [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix)
        [1.0.20] (with the testing fix)   [same as head's [1.0.20]]

   So the head branch's [1.0.20] is already in the base (master) and we don't need to add it again.

   The head branch's [1.0.21] (with the tformat: fix) is not in the base (master) because the base (master) has a different [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix). We want to incorporate the head branch's change for [1.0.21] into the base's [1.0.21]? 

   How? By adding the head branch's change as an additional bullet in the base's [1.0.21] section.

   Therefore, the resolved file should be:

        # Changelog

        ## [1.0.22] - 2026-05-22

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        ## [1.0.21] - 2026-05-21

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.
        * **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.

        ## [1.0.20] - 2026-05-20

        ### Changed
        * **Testing:** Fixed tuple unpacking bug in `TestArchitectureDetectorWalk` introduced by previous traversal optimizations. No dead code pruned.

        ## [1.0.19] - 2026-05-06

        ... and then the rest of the changelog from the base (or head, since they are the same from [1.0.19] down) ...

   But note: the base (master) has more than just these versions? We must include the entire changelog.

   However, we are not given the full changelog in the file versions (it's truncated). We must rely on the fact that the base (master) and head branch have the same changelog from [1.0.19] downwards.

   Therefore, we can take the base (master) changelog and then:

        - Insert the head branch's [1.0.21] change as an additional bullet in the existing [1.0.21] section (which is already in the base) and then we are done? 

   But wait, the base (master) already has [1.0.22] at the top, then [1.0.21] (with the CODEDNA_MAX_FILE_SIZE fix), then [1.0.20] (with the testing fix), then [1.0.19] etc.

   We want to change the [1.0.21] section to have two bullets.

   Alternatively, we can generate the merged changelog by:

        Start with the base (master) changelog.

        Then, for the [1.0.21] section, we add the head branch's change as an additional bullet.

   However, note: the head branch