workflow:

VM an pathfinder der LXC oder kvm class übergeben
	prüft ob vm vorhanden

snapshotCreate funktion aufrufen
	holt liste der disk-pfade über diskFinder
	fährt VM runter
		snapshot jedes elements
		start VM
		returned liste der snapshots

liste der snapshots an copySource2Target
	btrfs rotieren
	rsync oder raw bytes klonen
	

liste der snapshots an snapshotRemove funktion übergeben

btrfs dedup
