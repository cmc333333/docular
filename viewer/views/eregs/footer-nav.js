export function PrevSect({ prev }) {
  if (!prev) return null;

  return (
    <div>
      Previous section
    </div>
  );
}

export function NextSect({ next }) {
  if (!next) return null;

  return (
    <div>
      Next section
    </div>
  );
}

export default function FooterNav({ struct }) {
  console.log(struct);
  return (
    <section>
      <PrevSect prev={struct.meta.prev_doc } />
      <NextSect next={struct.meta.next_doc } />
    </section>
  );
}
